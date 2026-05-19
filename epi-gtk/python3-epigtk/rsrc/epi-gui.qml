import org.kde.plasma.core as PlasmaCore
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window

ApplicationWindow {

    property bool closing: false
    id:mainWindow
    visible: true
    title: "EPI"
    color:"#eff0f1"
    property int margin: 1
    width: mainLayout.implicitWidth + 2 * margin
    height: mainLayout.implicitHeight + 2 * margin
    minimumWidth: mainLayout.Layout.minimumWidth + 2 * margin
    minimumHeight: mainLayout.Layout.minimumHeight + 2 * margin
    Component.onCompleted: {
        x = Screen.width / 2 - width / 2
        y = Screen.height / 2 - height / 2
    }
    onClosing:(close)=> {
        close.accepted=closing;

        if (!closing) {
            mainStackBridge.closeApplication();
            closeTimer.start();
        }
        
    }

    Timer {
        id: closeTimer
        interval: 100
        repeat: true
        onTriggered: {
            if (mainStackBridge.closeGui) {
                stop();
                mainWindow.closing = true;
                mainWindow.close();
            }
        }
    }

    
    ColumnLayout {
        id: mainLayout
        anchors.fill: parent
        Layout.minimumWidth:800
        Layout.minimumHeight:580

        Rectangle{
            id: bannerBox
            color: "#000886"
            Layout.fillWidth:true
            Layout.preferredHeight: 120

            Image{
                id:banner
                source: "/usr/lib/python3/dist-packages/epigtk/rsrc/epi-banner.png"
                asynchronous: false
                anchors.centerIn: parent
                fillMode: Image.PreserveAspectFit  
            }
        }

        StackView {
            id: mainView
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.preferredHeight:460

            property int currentIndex: mainStackBridge.currentStack

            initialItem:loadingView

            onCurrentIndexChanged:{
                switch(currentIndex){
                    case 0:
                        mainView.replace(loadingView)
                        break;
                    case 1:
                        mainView.replace(errorView)
                        break;
                    case 2:
                        mainView.replace(applicationOptionView)
                        break
                }
            }

            replaceEnter: Transition {
                NumberAnimation {
                    property: "opacity"
                    from: 0
                    to: 1
                    duration: 60
                }
            }
            replaceExit: Transition {
                NumberAnimation { 
                    property: "opacity"
                    from: 1
                    to: 0
                    duration: 60
                }
            }
         
           Component{
               id:loadingView
               Loading{
                   id:loading
               }

           }

           Component{
            id:errorView
                ErrorPanel{
                    id:errorPanel
                }
            }

            Component{
                id:applicationOptionView
                ApplicationOptions{
                    id:applicationOptions
                }
            }
        }
    }
}

