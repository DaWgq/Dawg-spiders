(function ($) {

	function clearBr(key)
	{
	    key = key.replace(/<\/?.+?>/g,"");
	    key = key.replace(/[\r\n]/g, "");
	    return key;
	} 	
	
    var sessionHelper = {
        getSession: function (values,callback) {
            var result = getServerData({ "keys": "#" + JSON.stringify(values) }, "login/actions/getSession.xml", false).result;
            if(result) {
                for(var key in result) {
                    var keyValue=result[key];
                    if(keyValue) {
                        try {
                            keyValue=JSON.parse(keyValue);
                            result[key]=keyValue;
                        }catch(e) {
                        }
                    }
                }
            }
            if(callback && result) {
                result=callback(result);
            }
            return result;
//        	var rr=null;
//        	var jsonData={};
//        	jsonData.flag="get";
//            jsonData.v=values.join("||");
//	        $.ajax({
//	            url: __GlobalInfo.webroot+"/admin_client/tools/sessionHelper.jsp",
//	            data: jsonData,
//	            dataType: 'text',
//	            type: 'post',
//	            async: false,
//	            success: function (result) {
//	            	rr=result;
//	            	if(callback) rr=callback(result);
//	            }
//	        });
//	        return rr;
        },
		getApplication: function (values,callback) {
        	var rr=null;
        	var jsonData={};
        	jsonData.flag="getApplication";
            jsonData.v=values.join("||");
	        $.ajax({
	            url: __GlobalInfo.webroot+"/admin_client/tools/sessionHelper.jsp",
	            data: jsonData,
	            dataType: 'text',
	            type: 'post',
	            async: false,
	            success: function (result) {
	            	rr=result;
	            	if(callback) rr=callback(result);
	            }
	        });
	        return rr;
        },        
        getSessionResultProcess:function(valuestr) {
	        var obj=null;
	        if(valuestr) {
	        	valuestr=clearBr(valuestr);
	            var arrays=valuestr.split("||");
	            if(arrays.length>0) obj={};
	             for(var i=0;i<arrays.length;i++) {
	                 var item=arrays[i];
	                 if(item && (item.split("--")) && (item.split("--").length==2))  {
	                     var items=item.split("--");
	                     obj[items[0]]=items[1];
	                 }
	             }
	        }   
	        return obj;
        },
        setSession: function(items,callback) {
            getServerData({"items":"#"+JSON.stringify(items)},"admin_client/tools/module/setSession.xml",false,callback);

//            var jsonData={};
//            jsonData.flag="update";
//            var v="";
//            for(var key in items)
//            {
//                v=v+key+"--"+items[key]+"||";
//            }
//            if(v.endWith("||")) v= v.substring(0, v.length-2);
//            jsonData.v=v;
//            $.ajax({
//                url: __GlobalInfo.webroot+"/admin_client/tools/sessionHelper.jsp",
//                data: jsonData,
//                dataType: 'text',
//                type: 'post',
//                async: false,
//                success: function (result) {
//                   if(callback) {
//                   	callback();
//                   }
//                }
//            });
        }
    };  
    
    $.sessionHelper = sessionHelper;

})(jQuery);


