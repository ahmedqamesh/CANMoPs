// Copyright 2012 CrossControl

#include "canworkerthread.h"

#include "canwrapper.h"


#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/uio.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>

#include <signal.h>

#include <assert.h>

#include <errno.h>

#include <fcntl.h>

#include <stdio.h>

#include <sys/time.h>

CanWorkerThread::CanWorkerThread(QObject *parent) :
    QThread(parent)
{
}

// Setup worker thread
// Parameter:
// wrapper - pointer to CAN wrapper instance
void CanWorkerThread::Init(CanWrapper *wrapper)
{
    m_running = true;
    m_can = wrapper;
}

// This function will be excuted in an own thread when start is called from parent thread
// It will wait for data from CAN (blocking) and signal to GUI when data arrives
void CanWorkerThread::run()
{
    struct can_frame msg;
    int ret;
    int i;
    int errorCode;

    bool rtr;
    bool extended;
    bool error;

    struct timeval tv;

    tv.tv_sec = 1;
    tv.tv_usec = 0;

    while(m_running)
    {
        // This call will block but only for one sec to let us abort if m_running = false
        // errorCode is errors related to socket problems, error is can related problems like bus-off
        ret = m_can->GetMsg(msg, extended, rtr, error, errorCode, tv);

        if(ret)
        {
            QString string;

            if(error)   // Error frame
            {
                string = QString("Error frame received, class = " +  QString::number(msg.can_id));
            }
            else
            if(extended)   // Extended frame
            {
                if(rtr)
                {
                    string = QString("RTR ID: %1 LENGTH: %2").arg(msg.can_id).arg(msg.can_dlc);
                }
                else
                {
                    string = QString("ID: %1 LENGTH: %2 DATA: ").arg(msg.can_id).arg(msg.can_dlc);

                    for(i = 0; i < msg.can_dlc; i++)
                    {
                        string.append(QString::number(msg.data[i]) + " ");
                    }
                }
            }
            else    // Standard frame
            {
                if(rtr)
                {
                    string = QString("RTR ID: %1 LENGTH: %2").arg(msg.can_id).arg(msg.can_dlc);
                }
                else
                {
                    string = QString("ID: %1 LENGTH: %2 DATA: ").arg(msg.can_id).arg(msg.can_dlc);

                    for(i = 0; i < msg.can_dlc; i++)
                    {
                        string.append(QString::number(msg.data[i]) + " ");
                    }
                }
             }

            // Send string to GUI
            // Because this is an own thread, we must emit a signal rater than making a direct call
            // Because we are in a different thread than the GUI thread, this will put the data onto a queue
            // And will be processed by the GUI thread
            emit msgReceived(string);
        }
        else
        {
            if(errorCode)
            {
                QString string = QString("Error detected, errorcode: " + QString::number(errorCode));

                emit msgReceived(string);
            }
        }
    }
}

// Make thread to stop. Because the thread might be waiting on a blocking call, the call must be unblocked first to actually make the
// thread stop
void CanWorkerThread::shutDown()
{
    m_running = false;
}

