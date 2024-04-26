import QtQuick 2.15
import QtQml.Models 2.8

DelegateModel {
	id:filterModel
	property string role
	property string search
	property bool showDepend
	property string statusFilter
	onRoleChanged:Qt.callLater(update)
	onSearchChanged:Qt.callLater(update)
	onShowDependChanged:Qt.callLater(update)
	onStatusFilterChanged:Qt.callLater(update)
	property var visibleElements:[]
	
	groups: [
		DelegateModelGroup{
			id:allItems
			name:"all"
			includeByDefault:true
			onCountChanged:Qt.callLater(update)
		},
		DelegateModelGroup{
			id:visibleItems
			name:"visible"
		}
	]

	filterOnGroup:"visible"

	function update(){
		visibleElements=[]
		if (allItems.count>0){
			allItems.setGroups(0,allItems.count,[ "all"]);
			for (let index = 0; index < allItems.count; index++) {
	            let item = allItems.get(index).model;
	            let visible = item[role].toLowerCase().includes(search.toLowerCase());
	            let matchStatus=true
	            if (statusFilter!="all"){
	            	switch(statusFilter){
	            		case "available":
	            			if (item["status"]=="installed"){
	            				matchStatus=false
			            	}
			            	break;
			            case "installed":
			            	if (item["status"]=="available"){
			            		matchStatus=false
			            	}
			            	break;
			            case "error":
			            	if (item["resultProcess"]!=1){
			            		matchStatus=false
			            	}
			            	break
			       	}

			    }
	            if (!visible) continue;
	            if (!item["isVisible"] || !matchStatus) continue;
	            allItems.setGroups(index, 1, [ "all", "visible" ]);
	            visibleElements.push(index);
	            
	        }
    	}

	}
	Component.onCompleted: Qt.callLater(update)

}
