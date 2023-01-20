import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami

GridLayout{
    id: optionsGrid
    columns: 2
    flow: GridLayout.LeftToRight
    columnSpacing:10

    Rectangle{
        width:195
        Layout.minimumHeight:430
        Layout.preferredHeight:430
        Layout.fillHeight:true
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:4 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:packagesOption
                optionText:i18nd("epi-gtk","Information")
                optionIcon:"/usr/share/icons/breeze/actions/16/run-build.svg"
                Connections{
                    function onMenuOptionClicked(){
                        epiBridge.manageTransitions(0)
                    }
                }
            }

            MenuOptionBtn {
                id:detailsOption
                optionText:i18nd("epi-gtk","Process details")
                optionIcon:"/usr/share/icons/breeze/apps/16/utilities-terminal.svg"
                enabled:true
                Connections{
                    function onMenuOptionClicked(){
                        epiBridge.manageTransitions(1)
                    }
                }
            }

            MenuOptionBtn {
                id:helpOption
                optionText:i18nd("epi-gtk","Help")
                optionIcon:"/usr/share/icons/breeze/actions/16/help-contents.svg"
                Connections{
                    function onMenuOptionClicked(){
                        console.log("Ayuda");
                    }
                }
            }
        }
    }

    GridLayout{
        id: layoutGrid
        rows:3 
        flow: GridLayout.TopToBottom
        rowSpacing:0

        StackLayout {
            id: optionsLayout
            currentIndex:epiBridge.currentOptionsStack
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.alignment:Qt.AlignHCenter

            PackagesPanel{
                id:packagesPanel
            }
            KonsolePanel{
                id:konsolePanel
            }
 
        }

         Kirigami.InlineMessage {
            id: messageLabel
            visible:epiBridge.showStatusMessage[0]
            text:i18nd("epi-gtk","Test Text")
            type: {
                if (epiBridge.showStatusMessage[1]==""){
                    Kirigami.MessageType.Positive;
                }else{
                    Kirigami.MessageType.Error;
                }
            }
            Layout.minimumWidth:555
            Layout.fillWidth:true
            Layout.rightMargin:10
            
        }

        RowLayout{
            id:feedbackRow
            spacing:10
            Layout.topMargin:10
            Layout.bottomMargin:10
            Layout.fillWidth:true

            PC3.Button {
                id:uninstallBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"delete"
                text:i18nd("epi-gtk","Uninstall")
                Layout.preferredHeight:40
                Layout.rightMargin:10
                Keys.onReturnPressed: uninstallBtn.clicked()
                Keys.onEnterPressed: uninstallBtn.clicked()
                onClicked:{
                    console.log("Desintalar")
                }
            }

            Text{
                id:feedBackText
                text:getFeedBackText(1)
                visible:true
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                horizontalAlignment:Text.AlignHCenter
                Layout.preferredWidth:200
                Layout.fillWidth:true
                Layout.alignment:Qt.AlignHCenter
            }
               
            PC3.Button {
                id:installBtn
                visible:true
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text:i18nd("epi-gtk","Install")
                Layout.preferredHeight:40
                Layout.rightMargin:10
                Keys.onReturnPressed: installBtn.clicked()
                Keys.onEnterPressed: installBtn.clicked()
                onClicked:{
                    console.log("Instalar")
                }
            }
        }
    }
   

    Timer{
        id:timer
    }

    function delay(delayTime,cb){
        timer.interval=delayTime;
        timer.repeat=true;
        timer.triggered.connect(cb);
        timer.start()
    }
   
    function applyChanges(){
        delay(100, function() {
            if (epiBridge.endProcess){
                timer.stop()
                feedBackText.visible=false
                
            }else{
                if (epiBridge.endCurrentCommand){
                    epiBridge.getNewCommand()
                    var newCommand=epiBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }
            }
          })
    } 
 
    function getFeedBackText(code){

        var msg="";
        switch (code){
            case 1:
                msg=i18nd("epi-gtk","Removing Lliurex-Up lock file...");
                break;
            case 2:
                msg=i18nd("epi-gtk","Removing Dpkg lock file...");
                break;
            case 3:
                msg=i18nd("epi-gtk","Removing Apt lock file...");
                break;
             case 4:
                msg=i18nd("epi-gtk","Fixing the system...");
                break;
           
            default:
                break;
        }
        return msg;

    }

    
}

