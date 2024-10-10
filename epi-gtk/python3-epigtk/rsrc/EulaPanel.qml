import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtWebEngine


Rectangle {
    visible: true
    property alias eulaUrl:webEngine.url

    Component.onDestruction:{
        closeConnection()
    }


    WebEngineView {
        id:webEngine
        anchors.fill:parent
        url: eulaUrl
        profile.persistentCookiesPolicy:WebEngineProfile.NoPersistentCookies
                
    }

    function closeConnection(){
        webEngine.action(webEngine.Stop)

    }

}
