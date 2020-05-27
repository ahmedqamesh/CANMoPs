#-------------------------------------------------
#
# Project created by QtCreator 2012-03-17T01:34:20
#
#-------------------------------------------------

QT       += core gui

TARGET = SocketCANExample
TEMPLATE = app


SOURCES += main.cpp\
        mainwindow.cpp \
    canwrapper.cpp \
    canworkerthread.cpp

HEADERS  += mainwindow.h \
    canwrapper.h \
    canworkerthread.h

FORMS    += mainwindow.ui

target.path=/opt/SocketCAN/
INSTALLS += target
