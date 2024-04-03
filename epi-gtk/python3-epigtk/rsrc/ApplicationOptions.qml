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
                optionText:i18nd("epi-gtk","Home")
                optionIcon:"/usr/share/icons/breeze/places/22/user-home.svg"
                visible:true
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(0)
                        if (packageStackBridge.currentPkgOption==2){
                            packageStackBridge.showPkgInfo([1,""])
                        }
                    }
                }
            }

            MenuOptionBtn {
                id:detailsOption
                optionText:i18nd("epi-gtk","View details")
                optionIcon:"/usr/share/icons/breeze/apps/22/utilities-terminal.svg"
                visible:mainStackBridge.enableKonsole
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.manageTransitions(1)
                    }
                }
            }

            MenuOptionBtn {
                id:helpOption
                optionText:i18nd("epi-gtk","Help")
                optionIcon:"/usr/share/icons/breeze/actions/22/help-contents.svg"
                visible:{
                    if (packageStackBridge.wikiUrl!=""){
                        true
                    }else{
                        false
                    }
                }
                Connections{
                    function onMenuOptionClicked(){
                        mainStackBridge.openHelp()
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
            currentIndex:mainStackBridge.currentOptionsStack
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
            visible:mainStackBridge.showStatusMessage[0]
            text:getFeedBackText(mainStackBridge.showStatusMessage[1])
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
                   if (packageStackBridge.currentPkgOption==0){
                       if (mainStackBridge.showRemoveBtn){
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
                    switch (packageStackBridge.currentPkgOption){
                        case 0:
                            "remove"
                            break;
                        case 1:
                            "dialog-cancel"
                            break;
                        case 2:
                            "arrow-left"
                            break;
                    }
                }
                text:{
                    switch (packageStackBridge.currentPkgOption){
                        case 0:
                            i18nd("epi-gtk","Uninstall")
                            break;
                        case 1:
                            i18nd("epi-gtk","Reject Eula")
                            break;
                        case 2:
                            i18nd("epi-gtk","Back")
                            break;
                    }
                }
                enabled:{
                    if (mainStackBridge.enableRemoveBtn){
                        true
                    }else{
                        if (packageStackBridge.currentPkgOption==2){
                            true
                        }else{
                            false
                        }
                    }
                }

                Layout.preferredHeight:40
                Layout.rightMargin:10
                Keys.onReturnPressed: uninstallBtn.clicked()
                Keys.onEnterPressed: uninstallBtn.clicked()
                onClicked:{
                    switch (packageStackBridge.currentPkgOption){
                        case 0:
                            uninstallDialog.open()
                            break;
                        case 1:
                            packageStackBridge.rejectEula()
                            break;
                        case 2:
                            packageStackBridge.showPkgInfo([1,""])
                            break;
                    }
                }
            }
             ColumnLayout{
                id:feedbackColumn
                spacing:10
                Layout.alignment:Qt.AlignHCenter
                Text{
                    id:feedBackText
                    text:getFeedBackText(mainStackBridge.feedbackCode)
                    visible:true
                    font.family: "Quattrocento Sans Bold"
                    font.pointSize: 10
                    horizontalAlignment:Text.AlignHCenter
                    Layout.preferredWidth:200
                    Layout.fillWidth:true
                    Layout.alignment:Qt.AlignHCenter
                    wrapMode: Text.WordWrap
                }
                
                ProgressBar{
                    id:feedBackBar
                    indeterminate:true
                    visible:mainStackBridge.isProgressBarVisible
                    implicitWidth:100
                    Layout.alignment:Qt.AlignHCenter
                }
                
            }
               
            PC3.Button {
                id:installBtn
                visible:{
                    if (packageStackBridge.currentPkgOption!=2){
                        true
                    }else{
                        false
                    }
                }
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text:{
                    switch (packageStackBridge.currentPkgOption){
                        case 0:
                            if (packageStackBridge.isAllInstalled){
                                i18nd("epi-gtk","Reinstall")
                            }else{
                                i18nd("epi-gtk","Install")
                            }
                            break;
                        case 1:
                            i18nd("epi-gtk","Accept Eula")
                            break;
                        case 2:
                            ""
                            break;
                    }
                }
                enabled:{
                    if (mainStackBridge.enableApplyBtn){
                        true
                  }else{
                        false
                    }
                }
                Layout.preferredHeight:40
                Layout.leftMargin:10
                Layout.rightMargin:10
                Keys.onReturnPressed: installBtn.clicked()
                Keys.onEnterPressed: installBtn.clicked()
                onClicked:{
                    if (packageStackBridge.currentPkgOption==0){
                        konsolePanel.runCommand('history -c\n')
                        applyChanges()
                        mainStackBridge.launchInstallProcess()
                    }else{
                        konsolePanel.runCommand('history -c\n')
                        applyChanges()
                        packageStackBridge.acceptEula()
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
        dialogWidth:350
        btnAcceptVisible:true
        btnCancelText:i18nd("epi-gtk","Cancel")
        btnCancelIcon:"dialog-cancel"

        Connections{
            target:uninstallDialog
            function onDialogApplyClicked(){
                uninstallDialog.close()
                konsolePanel.runCommand('history -c\n')
                applyChanges()
                mainStackBridge.launchUninstallProcess()
            }
            function onCancelDialogClicked(){
                uninstallDialog.close()
            } 

        }        
    }

    CustomDialog{
        id:closeDialog
        dialogIcon:"/usr/share/icons/breeze/status/64/dialog-warning.svg"
        dialogTitle:"EPI"
        dialogMsg:i18nd("epi-gtk","It seems that the installation/uninstallation process has not finished yet?\nIf you close EPI the process will be closed.\nDo you want to close EPI?") 
        dialogWidth:600
        dialogVisible:mainStackBridge.showCloseDialog
        btnAcceptVisible:true
        btnCancelText:i18nd("epi-gtk","Cancel")
        btnCancelIcon:"dialog-cancel"

        Connections{
            target:closeDialog
            function onDialogApplyClicked(){
                mainStackBridge.forceClossing()
            }
            function onCancelDialogClicked(){
                closeTimer.stop()
                mainStackBridge.cancelClossing()
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
            if (mainStackBridge.endProcess){
                timer.stop()
                
            }else{
                if (mainStackBridge.endCurrentCommand){
                    mainStackBridge.getNewCommand()
                    var newCommand=mainStackBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }
            }
          })
    } 
 
    function getFeedBackText(code){

        var msg="";
        var errorHeaded=i18nd("epi-gtk","The selected applications cannot be uninstalled.\n")
        var warningHeaded=i18nd("epi-gtk","Some selected application successfully uninstalled.\nOthers not because ")
        switch (code){
            case -14:
                msg=i18nd("epi-gtk","Internet connection not detected")
                break;
            case -15:
                msg=errorHeaded+i18nd("epi-gtk","It is part of the system meta-package");
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
            case -21:
                msg=errorHeaded+i18nd("epi-gtk","You do not have permissions to perfom this action")
                break;
            case -22:
                msg=errorHeaded+i18nd("epi-gtk","Action blocked due to insufficient permissions and meta-package protection")
                break;
            case -23:
                msg=i18nd("epi-gtk","The installation process ended with errors")
                break;
            case 3:
                msg=i18nd("epi-gtk","Checking internet connection. Wait a moment...");
                break;
            case 4:
                msg=i18nd("epi-gtk","Application already installed");
                break;
            case 5:
                msg=i18nd("epi-gtk","It seems that the packages were installed without using EPI.\nIt may be necessary to run EPI for proper operation");
                break;
            case 6:
                msg=i18nd("epi-gtk","It seems that the packages were installed but the execution of EPI failed.\nIt may be necessary to run EPI for proper operation");
                break;
            case 7:
                msg=i18nd("epi-gtk","Showing the end user license agreement for:\n")+packageStackBridge.currentEulaPkg;
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
                msg=warningHeaded+i18nd("epi-gtk","they are part of the system's meta-package");
                break;
            case 20:
                msg=i18nd("epi-gtk","Searching information.Wait a moment...")
                break;
            case 21:
                msg=i18nd("epi-gtk","Information not availabled")
                break;
            case 22:
                msg=warningHeaded+i18nd("epi-gtk","you do not have permissions to uninstall them")
                break;
            case 23:
                msg=warningHeaded+i18nd("epi-gtk","you do not have permissions and meta-package protection")
                break;
            default:
                break;
        }
        return msg;
    }

    function getMsgType(){

        switch(mainStackBridge.showStatusMessage[2]){
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

