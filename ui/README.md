# UI Development

## Developer Tools

Donwload and install the latest community edition of Qt Creator from here: https://www.qt.io/offline-installers

a few install notes:    

* The installer requires a free Qt account
* Take care to claim pindividual ersonal use, and not enterprise

Reference documentation for the Qt Creator is here: https://doc.qt.io/qtcreator/

And a sub section widget based apps such as this one is here: https://doc.qt.io/qtcreator/creator-using-qt-designer.html

## Developer Guide

First, do not manually edit the form.ui file in Qt Creator or anyhwere else. This is a automatically generated file based on the design in Qt Creator and should not be changed outside that context.

#### To start: 
* Launch Qt Creator
* Open the form.ui file | File -> Open File or Project... (Ctrl + O)
* Click Design on the left side control panel

#### To edit existing objects in the UI:
* Click on the UI element in the preview window
    * or find it by name in the upper right object window
* View and edit properties of the selected object in the lower right window.
    * QObject.objectName is the name used in typescript code.
    * QWidget are UI properties includeing styleSheet for CSS
    * Other categories will include sub class properties specific to the type of object in the UI.
* Save your work | File -> Save "form.ui" (Ctrl + S)

#### To add objects to the UI:
* Click on an element in the left window, drag to the preview window, and drop where desired.
* View the new object in the right side windows.
    * Take care to ensure the element is named well and in the correct layout.
    * Tip: in the lower right window, properties changed from default will be bold. Use this to determine what should be added to a new element to match style.


### Developer Tour

There are three main components to this application

1. control_frame: lays out various control knobs, each in their own frame.

2. keys_frame: lays out each key on the synthesizer

3. wave_frame: lays out the wave selection radio buttons

### Typescript

In form.load_ui() the file is loaded into a QWidget object.
This object can be used to manipulate the UI within the application.

