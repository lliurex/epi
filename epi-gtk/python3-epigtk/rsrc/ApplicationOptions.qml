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
        width:130
        Layout.minimumHeight:460
        Layout.preferredHeight:460
        Layout.fillHeight:true
        border.color: "#d3d3d3"

        GridLayout{
            id: menuGrid
            rows:4 
            flow: GridLayout.TopToBottom
            rowSpacing:0

            MenuOptionBtn {
                id:packagesOption
                optionText:i18nd("epi-gtk","Init")
                optionIcon:"/usr/share/icons/breeze/places/16/user-home.svg"
                optionVisible:true
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
                optionVisible:true
                enabled:epiBridge.enableKonsole
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
                optionVisible:{
                    if (epiBridge.wikiUrl!=""){
                        true
                    }else{
                        false
                    }
                }
                Connections{
                    function onMenuOptionClicked(){
                        epiBridge.openHelp()
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
            text:getFeedBackText(epiBridge.showStatusMessage[1])
            type:getMsgType()
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
                visible:{
                    if (epiBridge.currentPkgOption==0){
                        if (epiBridge.showRemoveBtn){
                            true
                        }else{
                            false
                        }
                    }else{
                        true
                    }
                }
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:{
                   if (epiBridge.currentPkgOption==0){
                        "remove"
                    }else{
                        "dialog-cancel"
                    }
                }
                text:{
                    if (epiBridge.currentPkgOption==0){
                        i18nd("epi-gtk","Uninstall")
                    }else{
                        i18nd("epi-gtk","Reject Eula")
                    }
                }
                enabled:{
                    if (epiBridge.enableRemoveBtn){
                        true
                   }else{
                        false
                   }
                }

                Layout.preferredHeight:40
                Layout.rightMargin:10
                Keys.onReturnPressed: uninstallBtn.clicked()
                Keys.onEnterPressed: uninstallBtn.clicked()
                onClicked:{
                    if (epiBridge.currentPkgOption==0){
                        uninstallDialog.open()
                    }else{
                        epiBridge.rejectEula()
                    }
                }
            }

            Text{
                id:feedBackText
                text:getFeedBackText(epiBridge.feedbackCode)
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
                text:{
                    if (epiBridge.currentPkgOption==0){
                        i18nd("epi-gtk","Install")
                    }else{
                        i18nd("epi-gtk","Accept Eula")
                    }
                }
                enabled:{
                    if (epiBridge.enableApplyBtn){
                        true
                  }else{
                        false
                    }
                }
                Layout.preferredHeight:40
                Layout.rightMargin:10
                Keys.onReturnPressed: installBtn.clicked()
                Keys.onEnterPressed: installBtn.clicked()
                onClicked:{
                    if (epiBridge.currentPkgOption==0){
                        applyChanges()
                        epiBridge.launchInstallProcess()
                    }else{
                        applyChanges()
                        epiBridge.acceptEula()
                    }
     
                }
            }
        }
    }
   
    CustomDialog{
        id:uninstallDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"EPI"+" - "+i18nd("epi-gtk","Uninstall process")
        dialogMsg:i18nd("epi-gtk","Do you want uninstall the application?") 
        dialogWidth:300
        btnAcceptVisible:true
        btnCancelText:i18nd("epi-gtk","Cancel")
        btnCancelIcon:"dialog-cancel"

        Connections{
            target:uninstallDialog
            function onDialogApplyClicked(){
                uninstallDialog.close()
                applyChanges()
                epiBridge.launchUninstallProcess()
            }
            function onCancelDialogClicked(){
                uninstallDialog.close()
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
            if (epiBridge.endProccess){
                timer.stop()
                /*feedBackText.visible=false*/
                
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
            case -14:
                msg=i18nd("epi-gtk","Internet connection not detected")
                break;
            case -15:
                msg=i18nd("epi-gtk","The selected applications cannot be uninstalled.\nIt is part of the system meta-package");
                break;
            case -16:
                msg=i18nd("epi-gtk","Uninstalled process ending with errors");
                break;
            case -17:
                msg=i18nd("epi-gtk","Installation aborted. Error preparing system")
                break;
            case -18:
                msg=i18nd("epi-gtk","Installation aborted. Unable to download package")
                break;
            case -19:
                msg=i18nd("epi-gtk","Installation aborted. Error installing application")
                break;
            case -20:
                msg=i18nd("epi-gtk","Installation aborted. Error ending installation")
                break;
            case 3:
                msg=i18nd("epi-gtk","Checking internet connection. Wait a moment...");
                break;
            case 4:
                msg=i18nd("epi-gtk","Application already installed");
                break;
            case 5:
                msg=i18nd("epi-gtk","It seems that the packages were installed without using EPI.\nIt may be necessary to run EPI for proper operation");
            case 6:
                msg=i18nd("epi-gtk","It seems that the packages were installed but the execution of EPI failed.\nIt may be necessary to run EPI for proper operation");
                break;
            case 7:
                msg=i18nd("epi-gtk","Showing the end user license agreement for: ")+epiBridge.currentEulaPkg;
                break;
            case 8:
                msg=i18nd("epi-gtk","Checking if repositories need updating...")
                break;
            case 9:
                msg=i18nd("epi-gtk","Checking system architecture...")
                break;
            case 10:
                msg=i18nd("epi-gtk","Gathering Information...")
                break;
            case 11:
                msg=i18nd("epi-gtk","Downloading application...")
                break;
            case 12:
                msg=i18nd("epi-gtk","Preparing installation...")
                break;
            case 13:
                msg=i18nd("epi-gtk","Installing application...")
                break;
            case 14:
                msg=i18nd("epi-gtk","Ending the installation...")
                break;
            case 15:
                msg=i18nd("epi-gtk","Installation completed successfully")
                break;
            case 16:
                msg=i18nd("epi-gtk","Checking if selected applications can be uninstalled...")
                break;
            case 17:
                msg=i18nd("epi-gtk","Uninstall selected applications. Wait a moment...")
                break;
            case 18:
                msg=i18nd("epi-gtk","Applications successfully uninstalled");
                break;
            case 19:
                msg=i18nd("epi-gtk","Some selected application successfully uninstalled.\nOthers not because they are part of the system's meta-package");
                break;
            default:
                break;
        }
        return msg;
    }

    function getMsgType(){

        switch(epiBridge.showStatusMessage[2]){
            case "Ok":
                return Kirigami.MessageType.Positive;
            case "Error":
                return Kirigami.MessageType.Error;
            case "Info":
                return Kirigami.MessageType.Information;
            case "Warning":
                return Kirigami.MessageType.Warning;
        }
    }

}

