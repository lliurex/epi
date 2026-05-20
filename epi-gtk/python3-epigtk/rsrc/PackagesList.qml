import QtQuick
import QtQuick.Controls
import QtQml.Models 2.8
import org.kde.plasma.components as PC
import org.kde.kirigami as Kirigami
import QtQuick.Layouts


Rectangle{
    id: optionsGrid
    property alias packagesModel:filterModel.model
    property alias listCount:listPkg.count
    Layout.fillWidth:true
    Layout.fillHeight:true
    color:"transparent"

    ColumnLayout{
        id:mainGrid
        anchors.fill:parent
        spacing:10

        RowLayout{
            Layout.alignment:Qt.AlignRight
            spacing:10
            Layout.topMargin:packageStackBridge.selectPkg?15:0

            PC.Button{
                id:statusFilterBtn
                display:AbstractButton.IconOnly
                icon.name:"view-filter"
                visible:packageStackBridge.selectPkg
                enabled:packageStackBridge.totalErrorInProcess==0 &&
                        packageStackBridge.enablePkgList &&
                        !packageStackBridge.isAllInstalled.allInstalled &&
                        !packageStackBridge.isAllInstalled.allAvailable

                
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
                        enabled:packageStackBridge.filterStatusValue!="installed"?true:false
                        onClicked:packageStackBridge.manageStatusFilter("installed")
                    }

                    PC.MenuItem{
                        icon.name:"noninstalled"
                        text:i18nd("epi-gtk","Show uninstalled apps")
                        enabled:packageStackBridge.filterStatusValue!="available"?true:false
                        onClicked:packageStackBridge.manageStatusFilter("available")
                    }
                    PC.MenuItem{
                        icon.name:"emblem-error"
                        text:i18nd("epi-gtk","Show apps with error")
                        enabled: packageStackBridge.filterStatusValue!="error" &&
                                 packageStackBridge.totalErrorInProcess>0

                        onClicked:packageStackBridge.manageStatusFilter("error")
                    }
                    PC.MenuItem{
                        icon.name:"kt-remove-filters"
                        text:i18nd("epi-gtk","Remove filter")
                        enabled:packageStackBridge.filterStatusValue!="all"?true:false
                        onClicked:packageStackBridge.manageStatusFilter("all")
                    }
                }
            }
                
            PC.TextField{
                id:pkgSearchEntry
                font.pointSize:10
                horizontalAlignment:TextInput.AlignLeft
                focus:true
                width:100
                text:packageStackBridge.appFromStore
                visible:packageStackBridge.selectPkg
                enabled:packageStackBridge.enablePkgList
                placeholderText:i18nd("epi-gtk","Search...")
             }
        }

        Rectangle {
            id:pkgTable
            visible: true
            color:"white"
            Layout.fillHeight:true
            Layout.fillWidth:true
            Layout.topMargin:packageStackBridge.selectPkg?0:40
  
            border.color: "#d3d3d3"

            PC.ScrollView{
                anchors.fill:parent
       
                ListView{
                    id: listPkg

                    Timer {
                        id: searchTimer
                        interval: 150
                        repeat: false
                        onTriggered: filterModel.update()
                    }

                    model:FilterDelegateModel{
                        id:filterModel
                        model:packagesModel
                        role:"metaInfo"
                        showDepend:packageStackBridge.showDependEpi
                        search:pkgSearchEntry.text.trim()
                        statusFilter:packageStackBridge.filterStatusValue
                        externalTimer: searchTimer
                        
                        delegate: ListDelegatePkgItem{
                            width:listPkg.width
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

                    currentIndex:-1
                    clip: true
                    focus:true
                    boundsBehavior: Flickable.StopAtBounds
                    highlight: Rectangle { 
                        color: Kirigami.Theme.highlightColor
                        opacity: 0.3
                    }
                    highlightMoveDuration: 0
                    highlightResizeDuration: 0
                   

                    Kirigami.PlaceholderMessage { 
                        id: emptyHint
                        anchors.centerIn: parent
                        width: parent.width - (Kirigami.Units.largeSpacing * 4)
                        visible: listPkg.count==0?true:false
                        text: (pkgSearchEntry.text !== "" || 
                              packageStackBridge.filterStatusValue !== "all") 
                                ? i18nd("epi-gtk", "Applications not found") 
                                : i18nd("epi-gtk", "Loading application list...")
                        icon.name:"epi-gtk"
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
                icon.name:packageStackBridge.uncheckAll?"list-remove":"list-add"
                text: packageStackBridge.uncheckAll?i18nd("epi-gtk","Uncheck all packages"):i18nd("epi-gtk","Check all packages")
                enabled:packageStackBridge.enablePkgList

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
                font.pointSize: 10
                horizontalAlignment:Text.AlignLeft
                Layout.fillWidth:true
                Layout.alignment:Qt.AlignLeft
            }
        }      
    }

}

