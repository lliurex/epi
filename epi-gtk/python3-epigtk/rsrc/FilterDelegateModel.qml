import QtQuick
import QtQml.Models

DelegateModel {
	id:filterModel
	property var externalTimer: null
	property string role: ""
	property string search:""
	property bool showDepend:false
	property string statusFilter
	onRoleChanged:if (externalTimer) externalTimer.restart()
	onSearchChanged:if (externalTimer) externalTimer.restart()
	onShowDependChanged:if (externalTimer) externalTimer.restart()
	onStatusFilterChanged:if (externalTimer) externalTimer.restart()
	property var visibleElements:[]
	
	groups: [
		DelegateModelGroup{
			id:allItems
			name:"all"
			includeByDefault:true
			onCountChanged:if (externalTimer) externalTimer.restart()
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
	Component.onCompleted: if (externalTimer) externalTimer.restart()

}
