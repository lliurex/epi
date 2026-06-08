import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Dialogs 1.3
import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami

RowLayout{
    id: optionsGrid
    spacing:10

    Rectangle{
        width:130
        Layout.fillHeight:true
        border.color: palette.mid

        ColumnLayout{
            id: menuGrid
            anchors.fill:parent
            spacing: 0

            MenuOptionBtn {
                id:packagesOption
                optionText:i18nd("epi-gtk","Home")
                optionIcon:"user-home"
                visible:true
                onMenuOptionClicked:{
                    mainStackBridge.manageTransitions(0)
                    if (packageStackBridge.currentPkgOption==2){
                        packageStackBridge.showPkgInfo([1,""])
                    }
                }
            }

            MenuOptionBtn {
                id:detailsOption
                optionText:i18nd("epi-gtk","View details")
                optionIcon:"utilities-terminal"
                visible:mainStackBridge.enableKonsole
                onMenuOptionClicked:mainStackBridge.manageTransitions(1)
            }

            MenuOptionBtn {
                id:helpOption
                optionText:i18nd("epi-gtk","Help")
                optionIcon:"help-contents"
                visible:packageStackBridge.wikiUrl!=""?true:false
                onMenuOptionClicked:mainStackBridge.openHelp()
            }

            Item {
                Layout.fillHeight:true
            }
        }
    }

    ColumnLayout{
        id: layoutGrid
        Layout.fillWidth: true
        Layout.fillHeight: true
        spacing:0

        StackLayout {
            id: optionsLayout
            currentIndex:mainStackBridge.currentOptionsStack
            Layout.fillHeight:true
            Layout.fillWidth:true

            PackagesPanel{
                id:packagesPanel
            }
            KonsolePanel{
                id:konsolePanel
            }
        }

        Kirigami.InlineMessage {
            id: messageLabel
            visible:mainStackBridge.showStatusMessage["show"]
            text:getFeedBackText(mainStackBridge.showStatusMessage["msgCode"])
            type:getMsgType()
            Layout.fillWidth:true
            Layout.rightMargin:10
        }

        RowLayout{
            id:feedbackRow
            spacing:10
            Layout.leftMargin:5
            Layout.rightMargin:5
            Layout.topMargin:15
            Layout.bottomMargin:15
            Layout.fillWidth:true

            PC3.Button {
                id:uninstallBtn
                visible: packageStackBridge.currentPkgOption!==0 ||
                         mainStackBridge.showRemoveBtn
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:{
                    switch (packageStackBridge.currentPkgOption){
                        case 0:
                            return "remove"
                        case 1:
                            return "dialog-cancel"
                        case 2:
                            return "arrow-left"
                    }
                }
                text:{
                    switch (packageStackBridge.currentPkgOption){
                        case 0:
                            return i18nd("epi-gtk","Uninstall")
                        case 1:
                            return i18nd("epi-gtk","Reject Eula")
                        case 2:
                            return i18nd("epi-gtk","Back")
                    }
                }
                enabled: mainStackBridge.enableRemoveBtn ||
                         (packageStackBridge.currentPkgOption==2)
                 
                Layout.rightMargin:10
                Keys.onReturnPressed: uninstallBtn.clicked()
                Keys.onEnterPressed: uninstallBtn.clicked()
                onClicked:{
                    switch (packageStackBridge.currentPkgOption){
                        case 0:
                            uninstallDialog.open()
                            break
                        case 1:
                            packageStackBridge.rejectEula()
                            break
                        case 2:
                            packageStackBridge.showPkgInfo([1,""])
                            break
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
                    font.pointSize: 10
                    horizontalAlignment:Text.AlignHCenter
                    Layout.preferredWidth:200
                    Layout.fillWidth:true
                    Layout.alignment:Qt.AlignHCenter
                    wrapMode: Text.WordWrap
                }
                Item{
                    id:feedBackBar
                    visible:mainStackBridge.isProgressBarVisible
                    implicitWidth:100
                    implicitHeight:5
                    Layout.alignment:Qt.AlignHCenter

                    Rectangle{
                        anchors.fill:parent
                        color:"#E0E0E0"
                        clip:true

                        Rectangle{
                            id:bar
                            width:parent.width*0.2
                            height:parent.height
                            color:"#2196F3"
                            x:0
                        }    
                    }
                    Timer{
                        running:feedBackBar.visible
                        repeat:true
                        interval:60
                        onTriggered:{
                            if (feedBackBar.visible){
                                bar.x+=4;
                                if (bar.x > customPB.width){
                                    bar.x=-bar.width
                                }
                            }else{
                                stop()
                            }   
                        }
                    }
                }
            }

            PC3.Button {
                id:installBtn
                visible: packageStackBridge.currentPkgOption!==2
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:"dialog-ok"
                text:{
                    switch (packageStackBridge.currentPkgOption){
                        case 0:
                            if (packageStackBridge.isAllInstalled["allInstalled"]){
                                return i18nd("epi-gtk","Reinstall")
                            }else{
                                return i18nd("epi-gtk","Install")
                            }
                        case 1:
                            return i18nd("epi-gtk","Accept Eula")
                        case 2:
                            return ""
                    }
                }
                enabled:mainStackBridge.enableApplyBtn?true:false
                Layout.leftMargin:10
                Layout.rightMargin:10
                Keys.onReturnPressed: installBtn.clicked()
                Keys.onEnterPressed: installBtn.clicked()
                onClicked:{
                    konsolePanel.runCommand('history -c\n')
                    applyChanges()
                    if (packageStackBridge.currentPkgOption==0){
                         mainStackBridge.launchInstallProcess()
                    }else{
                         packageStackBridge.acceptEula()
                    }
                }
            }
        }
    }

    CustomDialog{
        id:uninstallDialog
        dialogIcon:"dialog-warning"
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
        interval:100
        repeat:true
        onTriggered:{
            if (mainStackBridge.endProcess){
                timer.stop()
            }else{
                if (mainStackBridge.endCurrentCommand){
                    mainStackBridge.getNewCommand()
                    var newCommand=mainStackBridge.currentCommand
                    konsolePanel.runCommand(newCommand)
                }  
            }
        }
    }

    function applyChanges(){
        timer.restart()
    }

    function getFeedBackText(code){

        var errorHeaded=i18nd("epi-gtk","The selected applications cannot be uninstalled.\n")
        var warningHeaded=i18nd("epi-gtk","Some selected application successfully uninstalled.\nOthers not because ")

        switch (code){
            case -14:
                return i18nd("epi-gtk","Internet connection not detected")
            case -15:
                return errorHeaded+i18nd("epi-gtk","It is part of the system meta-package")
            case -16:
                return i18nd("epi-gtk","Uninstalled process ending with errors")
            case -17:
                return i18nd("epi-gtk","Installation aborted. Error preparing system")
            case -18:
                return i18nd("epi-gtk","Installation aborted. Unable to download package")
            case -19:
                return i18nd("epi-gtk","Installation aborted. Error installing application")
            case -20:
                return i18nd("epi-gtk","Installation aborted. Error ending installation")
            case -21:
                return errorHeaded+i18nd("epi-gtk","You do not have permissions to perfom this action")
            case -22:
                return errorHeaded+i18nd("epi-gtk","Action blocked due to insufficient permissions and meta-package protection")
            case -23:
                return i18nd("epi-gtk","The installation process ended with errors")
            case 3:
                return i18nd("epi-gtk","Checking internet connection. Wait a moment...")
            case 4:
                return i18nd("epi-gtk","Application already installed");
            case 5:
                return i18nd("epi-gtk","It seems that the packages were installed without using EPI.\nIt may be necessary to run EPI for proper operation")
            case 6:
                return i18nd("epi-gtk","It seems that the packages were installed but the execution of EPI failed.\nIt may be necessary to run EPI for proper operation")
            case 7:
                return i18nd("epi-gtk","Showing the end user license agreement for:\n")+packageStackBridge.currentEulaPkg
            case 8:
                return i18nd("epi-gtk","Checking if repositories need updating...")
            case 9:
                return i18nd("epi-gtk","Checking system architecture...")
            case 10:
                return i18nd("epi-gtk","Gathering Information...")
            case 11:
                return i18nd("epi-gtk","Downloading application...")
            case 12:
                return i18nd("epi-gtk","Preparing installation...")
            case 13:
                return i18nd("epi-gtk","Installing application...")
            case 14:
                return i18nd("epi-gtk","Ending the installation...")
            case 15:
                return i18nd("epi-gtk","Installation completed successfully")
            case 16:
                return i18nd("epi-gtk","Checking if selected applications can be uninstalled...")
            case 17:
                return i18nd("epi-gtk","Uninstall selected applications. Wait a moment...")
            case 18:
                return i18nd("epi-gtk","Applications successfully uninstalled")
            case 19:
                return warningHeaded+i18nd("epi-gtk","they are part of the system's meta-package")
            case 20:
                return i18nd("epi-gtk","Searching information.Wait a moment...")
            case 21:
                return i18nd("epi-gtk","Information not availabled")
            case 22:
                return warningHeaded+i18nd("epi-gtk","you do not have permissions to uninstall them")
            case 23:
                return warningHeaded+i18nd("epi-gtk","you do not have permissions and meta-package protection")
            default:
                return ""
        }
    }

    function getMsgType(){

        switch(mainStackBridge.showStatusMessage["type"]){
            case 0:
                return Kirigami.MessageType.Positive
            case 1:
                return Kirigami.MessageType.Error
            case 2:
                return Kirigami.MessageType.Warning
            case 3:
            default:
                return Kirigami.MessageType.Information
        }
    }

    
}

