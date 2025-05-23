import QtQuick
import QtQuick.Controls
import QtQml.Models 2.8
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami
import QtQuick.Layouts


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
        RowLayout{
            Layout.alignment:Qt.AlignRight
            spacing:10
            Layout.topMargin:{
                if(packageStackBridge.selectPkg){
                    40
                }else{
                    0
                }
            }
            PC.Button{
                id:statusFilterBtn
                display:AbstractButton.IconOnly
                icon.name:"view-filter"
                visible:packageStackBridge.selectPkg
                enabled:{
                    if (packageStackBridge.totalErrorInProcess==0){
                        if (packageStackBridge.enablePkgList){
                            if (packageStackBridge.isAllInstalled[0] || packageStackBridge.isAllInstalled[1]){
                                false
                            }else{
                                true
                            }
                        }else{
                            false
                        }
                    }else{
                        true
                    }
                }
                ToolTip{
                    id:filterToolTip
                    delay: 1000
                    timeout: 3000
                    visible: statusFilterBtn.hovered
                    text:i18nd("epi-gtk","Click to filter applications by status")
                    background:Rectangle{
                    color:"#ffffff"
                    border.color:"#b8b9ba"
                    radius:5.0
                    }
                }
                onClicked:optionsMenu.open();
               
                PC.Menu{
                    id:optionsMenu
                    y: statusFilterBtn.height
                    x:-(optionsMenu.width-statusFilterBtn.width/2)

                    PC.MenuItem{
                        icon.name:"installed"
                        text:i18nd("epi-gtk","Show installed apps")
                        enabled:{
                            if (packageStackBridge.filterStatusValue!="installed"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:packageStackBridge.manageStatusFilter("installed")
                    }

                    PC.MenuItem{
                        icon.name:"noninstalled"
                        text:i18nd("epi-gtk","Show uninstalled apps")
                        enabled:
                            if (packageStackBridge.filterStatusValue!="available"){
                                true
                            }else{
                                false
                            }

                        onClicked:packageStackBridge.manageStatusFilter("available")
                    }
                    PC.MenuItem{
                        icon.name:"emblem-error"
                        text:i18nd("epi-gtk","Show apps with error")
                        enabled:
                            if (packageStackBridge.filterStatusValue!="error"){
                                if (packageStackBridge.totalErrorInProcess>0){
                                    true
                                }else{
                                    false
                                }
                            }else{
                                false
                            }

                        onClicked:packageStackBridge.manageStatusFilter("error")
                    }
                    PC.MenuItem{
                        icon.name:"kt-remove-filters"
                        text:i18nd("epi-gtk","Remove filter")
                        enabled:{
                            if (packageStackBridge.filterStatusValue!="all"){
                                true
                            }else{
                                false
                            }
                        }
                        onClicked:packageStackBridge.manageStatusFilter("all")
                    }
                }
            }
                
            PC.TextField{
                id:pkgSearchEntry
                font.pointSize:10
                horizontalAlignment:TextInput.AlignLeft
                Layout.alignment:Qt.AlignRight
                focus:true
                width:100
                text:packageStackBridge.appFromStore
                visible:packageStackBridge.selectPkg
                enabled:packageStackBridge.enablePkgList
                placeholderText:i18nd("epi-gtk","Search...")
                onTextChanged:{
                    filterModel.update()
                }
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

            PC.ScrollView{
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
                        role:"metaInfo"
                        showDepend:packageStackBridge.showDependEpi
                        search:pkgSearchEntry.text.trim()
                        statusFilter:packageStackBridge.filterStatusValue
                        
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
                            metaInfo:model.metaInfo

                        }
                    }

                    Kirigami.PlaceholderMessage { 
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (Kirigami.Units.largeSpacing * 4)
                        visible: listPkg.count==0?true:false
                        text: i18nd("epi-gtk","Applications not found")
                    }

                 } 
            }
        }
        RowLayout{
            Layout.fillWidth:true

            PC.Button {
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

