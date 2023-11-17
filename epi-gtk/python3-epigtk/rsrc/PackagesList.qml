import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQml.Models 2.8
import org.kde.plasma.components 2.0 as Components
import org.kde.plasma.components 3.0 as PC3
import org.kde.kirigami 2.16 as Kirigami
import QtQuick.Layouts 1.15


Rectangle{
    property alias packagesModel:filterModel.model
    property alias listCount:listPkg.count
    id: optionsGrid
    color:"transparent"

    GridLayout{
        id:mainGrid
        rows:3
        flow: GridLayout.TopToBottom
        rowSpacing:10
        anchors.left:parent.left
        anchors.fill:parent

        PC3.TextField{
            id:pkgSearchEntry
            font.pointSize:10
            horizontalAlignment:TextInput.AlignLeft
            Layout.alignment:Qt.AlignRight
            Layout.topMargin:40
            focus:true
            width:100
            visible:packageStackBridge.selectPkg
            enabled:packageStackBridge.enablePkgList
            placeholderText:i18nd("epi-gtk","Search...")
            onTextChanged:{
                filterModel.update()
            }
        }

        Rectangle {
            id:pkgTable
            visible: true
            color:"white"
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.topMargin:{
                if(packageStackBridge.selectPkg){
                    0
                }else{
                    40
                }
            }

            border.color: "#d3d3d3"

            PC3.ScrollView{
                implicitWidth:parent.width
                implicitHeight:parent.height
                anchors.leftMargin:10
       
                ListView{
                    id: listPkg
                    property int totalItems
                    anchors.fill:parent
                    height: parent.height
                    enabled:true
                    currentIndex:-1
                    clip: true
                    focus:true
                    boundsBehavior: Flickable.StopAtBounds
                    highlight: Rectangle { color: "#add8e6"; opacity:0.8;border.color:"#53a1c9" }
                    highlightMoveDuration: 0
                    highlightResizeDuration: 0
                    model:FilterDelegateModel{
                        id:filterModel
                        model:packagesModel
                        role:"customName"
                        showDepend:packageStackBridge.showDependEpi
                        search:pkgSearchEntry.text.trim()
                        
                        delegate: ListDelegatePkgItem{
                            width:pkgTable.width
                            pkgId:model.pkgId
                            showCb:model.showCb
                            isChecked:model.isChecked
                            customName:model.customName
                            pkgIcon:model.pkgIcon
                            status:model.status
                            isVisible:model.isVisible
                            resultProcess:model.resultProcess
                            order:model.order
                            showSpinner:model.showSpinner
                            entryPoint:model.entryPoint

                        }
                    }

                    Kirigami.PlaceholderMessage { 
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (units.largeSpacing * 4)
                        visible: listPkg.count==0?true:false
                        text: i18nd("epi-gtk","Applications not found")
                    }

                 } 
            }
        }
        RowLayout{
            Layout.fillWidth:true

            PC3.Button {
                id:selectBtn
                visible:packageStackBridge.selectPkg
                focus:true
                display:AbstractButton.TextBesideIcon
                icon.name:{
                    if (packageStackBridge.uncheckAll){
                        "list-remove"
                    }else{
                        "list-add"
                    }
                }
                text:{
                    if (packageStackBridge.uncheckAll){
                        i18nd("epi-gtk","Uncheck all packages")
                    }else{
                        i18nd("epi-gtk","Check all packages")
                    }
                }
                enabled:packageStackBridge.enablePkgList
                Layout.preferredHeight:40
                Layout.rightMargin:10
                Keys.onReturnPressed: selectBtn.clicked()
                Keys.onEnterPressed: selectBtn.clicked()
                onClicked:{
                    packageStackBridge.selectAll()
                }
            }

            Text{
                id:dependText
                text:i18nd("epi-gtk","(D) Addicitional application required")
                visible:packageStackBridge.showDependLabel
                font.family: "Quattrocento Sans Bold"
                font.pointSize: 10
                horizontalAlignment:Text.AlignLeft
                Layout.preferredWidth:200
                Layout.fillWidth:true
                Layout.alignment:Qt.AlignLeft
            }
        }      
    }

}

