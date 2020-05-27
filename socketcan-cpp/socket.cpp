/* A simple SocketCAN example */

#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <linux/can.h> // includes The basic CAN frame structure and the sockaddr structure
#include <linux/can/raw.h>

int soc;
int read_can_port;
struct can_frame frame;
struct sockaddr_can addr; // has an interface index like the  PF_PACKET socket, that also binds to a specific interface:
struct ifreq ifr;

int open_port(const char *port)
{
    /* open socket */
    /*
     1. you need to pass PF_CAN as the first argument to the socket system call
     2. there are two CAN protocols to choose from, the raw socket protocol and the broadcast manager (BCM).
     */
    // Step 1:  Create an empty socket API with PF_CAN as the protocol family:
    printf("Opening an  tempty socket API he socket with PF_CAN as the protocol family\n");
    soc = socket(PF_CAN, SOCK_RAW, CAN_RAW);
    //soc = socket(PF_CAN, SOCK_DGRAM, CAN_BCM);
    if(soc < 0)
    {
        return (-1);
    }
    //Step 2: Bind the socket to one of the interfaces (vcan0 or canx):
    printf("binding the socket %s to all CAN interfaces\n",port);
    addr.can_family = AF_CAN;
    strcpy(ifr.ifr_name, port);

    if (ioctl(soc, SIOCGIFINDEX, &ifr) < 0)
    {

        return (-1);
    }

    addr.can_ifindex = ifr.ifr_ifindex;

    fcntl(soc, F_SETFL, O_NONBLOCK);

    if (bind(soc, (struct sockaddr *)&addr, sizeof(addr)) < 0)
    {

        return (-1);
    }

    return 0;
}


int send_port(string option)
{
	printf("Writing CAN frames.... \n");
	socklen_t len = sizeof(addr);
	frame.can_id=0x601;
	frame.can_dlc=8;
	frame.data[0]=64;
	frame.data[1]=0;
	frame.data[2]=16;
	frame.data[3]=0;
	frame.data[4]=0;
	frame.data[5]=0;
	int retval;
	if (option =="recvfrom")
    {	//If CAN interface is bound to 'any' existing CAN interface (addr.can_ifindex = 0)
		//Recommended option if the information about the originating CAN interface is needed:
    	retval = recvfrom(soc, &frame, sizeof(struct can_frame), 0, (struct sockaddr*)&addr, &len);
    	/* get interface name of the received CAN frame */
        ifr.ifr_ifindex = addr.can_ifindex;
        ioctl(soc, SIOCGIFNAME, &ifr);
        printf("Received a CAN frame from interface %s\n", ifr.ifr_name);


    }
	/*
	if (option =="any")
	{
	        // To write CAN frames on sockets bound to 'any' CAN interface. The outgoing interface has to be defined certainly.
	        strcpy(ifr.ifr_name, "can0");
	        ioctl(soc, SIOCGIFINDEX, &ifr);
	        addr.can_ifindex = ifr.ifr_ifindex;
	        addr.can_family  = AF_CAN;
	        retval = sendto(soc, &frame, sizeof(struct can_frame), 0, (struct sockaddr*)&addr, sizeof(addr));
	        printf("Received a CAN frame from interface %s\n", ifr.ifr_name);
	    }
	*/

	else
	{
		retval = write(soc, &frame, sizeof(struct can_frame));
		printf("Received a CAN frame from interface %s\n", ifr.ifr_name);
	}

    if (retval != sizeof(struct can_frame))
    {
        return (-1);
    }
    else
    {
        return (0);
    }
}

/* this is just an example, run in a thread */
void read_port()
{	printf("Reading CAN frames.... \n");
    struct can_frame frame_rd;
    int recvbytes = 0;
    struct timeval tv;

    read_can_port = 1;

    while(read_can_port)
    {
        struct timeval timeout = {1, 0};
        fd_set readSet;
        FD_ZERO(&readSet);
        FD_SET(soc, &readSet);

        if (select((soc + 1), &readSet, NULL, NULL, &timeout) >= 0)
        {
            if (!read_can_port)
            {
                break;
            }
            if (FD_ISSET(soc, &readSet))
            {
                recvbytes = read(soc, &frame_rd, sizeof(struct can_frame));
                if(recvbytes)
                {
                	string data = "";
                	for (int i = 0; i<=sizeof(frame_rd.data); i++){
						data = data + frame_rd.data[i];
                	}
                	ioctl(soc, SIOCGSTAMP, &tv);
                	printf("ID = %d, dlc = %d, data = %s\n", frame_rd.can_id, frame_rd.can_dlc,data.c_str());

                }
            }
        }

    }

}

int close_port()
{
	printf("Closing the socket \n");
    close(soc);
    return 0;
}

int main(void)
{
    open_port("can0");
    send_port("write");
    read_port();
    close_port();
    return 0;
}
