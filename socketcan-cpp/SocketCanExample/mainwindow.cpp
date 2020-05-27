// Copyright 2012 CrossControl

#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <sys/uio.h>
#include <net/if.h>
#include <linux/can.h>
#include <linux/can/raw.h>

#include <QDebug>
#include <assert.h>
#include <stdio.h>

#include <QMessageBox>
#include <QString>

#include <canworkerthread.h>

#define BURSTSIZE 1000       // Size of message burst sent when pressing Send Burst

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    int ret;

    ui->setupUi(this);

    // Create class to handle CAN communication
    can = new CanWrapper();

    // Create a worker thread that listens to CAN messages and sends data to GUI with signal/slot mecanism
    m_workerThread = new CanWorkerThread();

    // connect signal from worker thread to slot in GUI
    ret = connect(m_workerThread, SIGNAL(msgReceived(QString)), this, SLOT(msgReceived(QString)));
    assert(ret);

    counter = 0;
    ui->comboBox->setCurrentIndex(1);

    timer10ms.setInterval(10);
    connect(&timer10ms, SIGNAL(timeout()), this, SLOT(on_sendButton_clicked()));




    // reset message counter
    m_receivedMessages = 0;

}

MainWindow::~MainWindow()
{
    // Tell worker thread to shut down
    m_workerThread->shutDown();

    // Close can connection
    can->Close();

    // wait for worker thread to shut down, force if problem
    if(!m_workerThread->wait(3000))
    {
        m_workerThread->terminate();
    }

    delete m_workerThread;
    delete can;
    delete ui;
}

// Message received from worker thread, add to list in GUI
void MainWindow::msgReceived(QString msg)
{
    // Append message to log
    ui->logEdit->appendPlainText(msg);

    // Increase message counter
    m_receivedMessages++;
    ui->label_2->setText(QString::number(m_receivedMessages));
}

// Send a single CAN message
void MainWindow::on_sendButton_clicked()
{
    int ret;
    struct can_frame msg;
    int i;
    QStringList list;
    int elements;
    int errorCode;
    bool extended;
    bool rtr;


    // Parse data to send from text box
    list = ui->dataEdit->text().split(" ", QString::SkipEmptyParts);
    elements = list.size();
    if(elements > 8)
    {
        elements = 8;
    }

    // Set data length
    msg.can_dlc = elements;

    // Get id from text box
    msg.can_id = counter++;//ui->idEdit->text().toInt();

    // Set data elements
    for(i = 0; i < elements; i++)
    {
        msg.data[i] = list[i].toInt();
    }

    rtr = ui->RTRcheckBox->checkState();
    extended = ui->ExtendedcheckBox->checkState();

    // Send CAN message on socket CAN
    ret = can->SendMsg(msg, extended, rtr, errorCode);

    // If send fails, show error dialog
    if(!ret)
    {
        qDebug() << "Could not send CAN message. Error code:" << QString::number(errorCode);

    }
}

// Send a burst of messages. This is used to test what happens if buffer overflows
void MainWindow::on_sendBurstButton_clicked()
{
  /*  struct can_frame msg;
    int i;
    int ret;
    int errorCode;

    msg.can_id = 0x100; // ID selected by random
    msg.can_dlc = 8;

    // Clear data
    for(i = 0; i < 8; i++)
    {
        msg.data[i] = 0;
    }

    // Send a burst of messages
    for(i = 0; i < BURSTSIZE; i++)
    {
        // First byte contains message number
        msg.data[0] = i;

        ret = can->SendMsg(msg, false, false, errorCode);
        usleep(1000);

        if(!ret)
        {
            QMessageBox msgBox;
            msgBox.setText("Could not send CAN message, aborting. Error code: " + QString::number(errorCode));
            msgBox.exec();

            // Quit loop at error
            return;
        }
    }
    */

           timer10ms.start();
}

// Change CAN net
void MainWindow::on_comboBox_currentIndexChanged(QString str)
{
    int ret;
    int errorCode;

    // Close old connection (if there is one) and shut down worker threads
    can->Close();

    // Tell thread to shut down, force if problem
    m_workerThread->shutDown();

    if(!m_workerThread->wait(3000))
    {
        m_workerThread->terminate();
    }

    // If user selected the CAN net "none" - do not open new CAN net
    if(str == "none")
        return;

    // Init new connection
    ret = can->Init(str.toUtf8(), errorCode);
    if(!ret)
    {
        QMessageBox msgBox;
        msgBox.setText("Could not initialize CAN net. Error code: " + QString::number(errorCode));
        msgBox.exec();

        return;
    }

    // Enable error messages to be reported
    can->EnableErrorMessages();

    // initialize worker thread
    m_workerThread->Init(can);

    // Start thread
    m_workerThread->start();
}

// Clear log
void MainWindow::on_clearButton_clicked()
{
    ui->logEdit->clear();

    m_receivedMessages = 0;
    ui->label_2->setText(QString::number(m_receivedMessages));
}

