// Copyright 2012 CrossControl

#ifndef CANWORKERTHREAD_H
#define CANWORKERTHREAD_H

#include <QThread>

#include "canwrapper.h"

class CanWorkerThread : public QThread
{
    Q_OBJECT
public:
    explicit CanWorkerThread(QObject *parent = 0);

    void Init(CanWrapper *wrapper); // Initialize

    void run();         // start thread

    void shutDown();    // Make thread shut down

signals:
    void msgReceived(QString msg);

public slots:

private:
    CanWrapper *m_can;  // Pointer to can wrapper class

    bool m_running;     // Set to false to stop thread



};

#endif // CANWORKERTHREAD_H
