import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtWebEngine 1.10


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
