// Copyright 2012 CrossControl

#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTimer>
#include <canworkerthread.h>

namespace Ui {
    class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

private slots:
    void on_comboBox_currentIndexChanged(QString);

    void on_clearButton_clicked();

    void on_sendBurstButton_clicked();

    void on_sendButton_clicked();

private:
    Ui::MainWindow *ui;                 // Main window

    QTimer timer10ms;
    int counter;

    CanWrapper *can;                    // Can wrapper class

    int m_receivedMessages;             // Number of received messages

    CanWorkerThread *m_workerThread;    // Thread that blocks and listens for CAN messages

public slots:
    void msgReceived(QString msg);
};

#endif // MAINWINDOW_H
