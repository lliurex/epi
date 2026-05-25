import QtQuick
import QtQuick.Controls
import QtWebEngine
import QtQuick.Layouts

Rectangle {
    visible: true
    property alias eulaUrl:webEngine.url

    Component.onDestruction:{
        closeConnection()
    }


    WebEngineView {
        id:webEngine
        anchors.fill:parent
        anchors.topMargin:15
        url: eulaUrl
        profile.persistentCookiesPolicy:WebEngineProfile.NoPersistentCookies
                
    }

    function closeConnection(){
        webEngine.action(webEngine.Stop)

    }

}
