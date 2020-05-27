// Copyright 2012 CrossControl

#include "canwrapper.h"

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/uio.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>

#include <assert.h>

#include <errno.h>

#include <fcntl.h>

#include <stdio.h>

#include <signal.h>

#include <linux/can/error.h>

#include <sys/time.h>

#include <sys/select.h>

#define INVALID_SOCKET -1

CanWrapper::CanWrapper()
{
    m_initialized = false;
    m_socket = INVALID_SOCKET;
}

// Initialize socket. Returns false if socket could not be opened.
// Parameters:
// interfaceName - the name of the CAN interface to open (can0, can1...)
// errorCode - error code indicating why init did fail
bool CanWrapper::Init(const char *interfaceName, int &errorCode)
{
    struct sockaddr_can addr;
    struct ifreq ifr;

    int ret;

    errorCode = 0;

    m_socket = socket(PF_CAN, SOCK_RAW, CAN_RAW);

    // Get index for a certain name
    strcpy(ifr.ifr_name, interfaceName);
    ret = ioctl(m_socket, SIOCGIFINDEX, &ifr);
    if(ret)
    {
        errorCode = errno;

        return false;
    }

    addr.can_family = AF_CAN;
    addr.can_ifindex = ifr.ifr_ifindex;

    ret = bind(m_socket, (struct sockaddr *)&addr, sizeof(addr));
    if(ret)
    {
        errorCode = errno;

        close(m_socket);
        m_socket = INVALID_SOCKET;

        return false;
    }

    m_initialized = true;

    return true;
}

// Close an open connection. Use when changing can net.
void CanWrapper::Close()
{
    if(m_initialized)
    {
        // We don't want to read or write anything more
        shutdown(m_socket, SHUT_RDWR);

        close(m_socket);

        m_socket = INVALID_SOCKET;

        m_initialized = false;
    }
}

// Send a message on the CAN-bus. Returns true if ok, false if not. Additional error info can be found in errorCode.
// Parameters:
// msg - the can message to send
// extended - set to true to send an extended frame
// rtr - set to true to send a remot request (rtr)
// errorcode - will be set to an error code
// Common errors:
//#define ENETDOWN        100     /* Network is down - use ifconfig up to start */
//#define EAGAIN          11      /* Try again - buffer is full */
//#define EBADF            9      /* Bad file number - can net not opened */

bool CanWrapper::SendMsg(struct can_frame msg, bool extended, bool rtr, int &errorCode)
{
    int res;

    errorCode = 0;

    if(!m_initialized)
        return false;


    if(extended)
    {
        msg.can_id |= CAN_EFF_FLAG;
    }

    if(rtr)
    {
        msg.can_id |= CAN_RTR_FLAG;
    }

    res = write(m_socket, &msg, sizeof(struct can_frame));

    if(res < 0)
    {
//        perror("could not send");
//        printf("errno is %d\r\n", errno);
        errorCode = errno;

        return false;
    }

    return true;
}

// Get a CAN message. If socket is blocking (default) - this call will block until data is received or until timeout period has expired.
// If socket is non blocking, it will return false if there is no data or if there is any error.
// If socket is blocking, it will return false if there is an error or at timeout.
// Parameters:
// frame - the received can frame
// extended - will be set to true if the received frame was an extended frame
// rtr - will be set to true if the received frame was an rtr frame
// errorcode - error code
// Common errors:
//#define ENETDOWN        100     /* Network is down - use ifconfig up to start*/
//#define EAGAIN          11      /* Try again - no data available*/
//#define EBADF            9      /* Bad file number - can net not opened */
// timeout - GetMsg will return false after timeout period
bool CanWrapper::GetMsg(struct can_frame &frame, bool &extended, bool &rtr, bool &error, int &errorCode, struct timeval timeout)
{
    int bytesRead;
    int ret;
    fd_set rfds;

    errorCode = 0;

    if(!m_initialized)
    {
        return false;
    }

    // Set up a file descriptor set only containing one socket
    FD_ZERO(&rfds);
    FD_SET(m_socket, &rfds);

    // Use select to be able to use a timeout
    ret = select(m_socket+1, &rfds, NULL, NULL, &timeout);
    if(ret < 0)
    {
        errorCode = errno;

        return false;
    }

    if(ret > 0)
    {
        bytesRead = read(m_socket, &frame, sizeof(frame));

        if(bytesRead < 0)
        {
            errorCode = errno;

            return false;
        }

        if(bytesRead == sizeof(frame))
        {
            error = frame.can_id & CAN_ERR_FLAG;

            extended = frame.can_id & CAN_EFF_FLAG;

            rtr = frame.can_id & CAN_RTR_FLAG;

            if(error)
            {
                frame.can_id  &= CAN_ERR_MASK;
            }

            if(extended)
            {
                frame.can_id  &= CAN_EFF_MASK;
            }
            else
            {
                frame.can_id &= CAN_SFF_MASK;
            }

            return true;
        }
    }

    return false;
}

// Set size of receive buffer. The standard size is usually large enough.
// Note that getsockopt will return twice the size set
// If settings a larger size than the system supports, the size will set to a lower value than requested
// Parameters:
// size - the requested size of the receive buffer
bool CanWrapper::SetRecvBufferSize(int size)
{
    int ret;
    int rcvbuf_size = size;

//    int rbuf;
//    int len = sizeof(int);

    // Print receive buf size before change
//    ret = getsockopt(m_socket,SOL_SOCKET,SO_RCVBUF,&rbuf,(socklen_t*)&len);
//    printf("receive buf size is before change: %d\r\n", rbuf);

    ret = setsockopt(m_socket, SOL_SOCKET, SO_RCVBUF, &rcvbuf_size, sizeof(rcvbuf_size));
    if(ret < 0)
    {
  //      perror("set recv buffer size");
  //      printf("errno is %d\r\n", errno);

        return false;
    }

    // Print receive buf size after change
//    ret = getsockopt(m_socket,SOL_SOCKET,SO_RCVBUF,&rbuf,(socklen_t*)&len);
//    printf("receive buf size is after change: %d\r\n", rbuf);

    return true;
}

// Configure the socket can layer to report errors
// see /linux/can/error.h for more options regading error handling (not implemented in this class).
void CanWrapper::EnableErrorMessages()
{
    int ret;

    can_err_mask_t err_mask = ( CAN_ERR_TX_TIMEOUT | CAN_ERR_BUSOFF );

    ret = setsockopt(m_socket, SOL_CAN_RAW, CAN_RAW_ERR_FILTER,
               &err_mask, sizeof(err_mask));
}
