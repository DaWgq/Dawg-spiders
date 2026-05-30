function isIE() {
    var navStr = navigator.userAgent.toLowerCase();
    if (navStr.indexOf("msie 10.0") !== -1 || navStr.indexOf("rv:11.0") !== -1) // 判断是IE10或者IE11
        return true;
    else
        return false;
}

var date = new Date();
var dateStr = date.getFullYear() + "" + (date.getMonth() + 1) + "" + date.getDate();
if (dateStr == '202044') {
    if (isIE()) {
        document.writeln("<script type='text/javascript' src='/scripts/grayscale.js'></script>")
    } else {
        document.writeln("<link rel='stylesheet' type='text/css' href='/scripts/grayscale.css'> ")
    }
}


$(function() {
    // var loac = window.location.href;
    // if (loac.indexOf("https") >= 0) {
    //     loac = loac.replace("https", "http");
    //     window.location.href = loac;
    //     return;
    // }
    var arryList = [
        "admin",
        "mobile_ticket",
        "ds_mobile",
        "account/hzhb_setexpert.html",
        "3dshoes",
        "alipay",
        "auth2",
        "ds-wx",
        "expert",
        "import",
        "live",
        "made",
        "maker-wx",
        "otherpage",
        "z-wx",
        "zapp",
        "ds_enter",
        "ds_bm",
        "z-demo",
        "admin_new",
        "quesnaire_mobile"
    ];
    for (var i in arryList) {
        if (window.location.href.indexOf(arryList[i]) > -1) {
            return;
        }
    }
    $("<link>").attr({
        rel: "stylesheet",
        type: "text/css",
        href: "https://www.cnmaker.org.cn/resource/css/kf.css"
    }).appendTo("head");
    //	$("body").append('<div class="rides-cs" id="floatTools" style="height: 265px;">\
    //          <div class="floatL">\
    //              <a title="查看在线客服" class="btnOpen" id="aFloatTools_Show" style="top: 20px; display: block;" href="javascript:void(0);">展开</a>\
    //              <a title="关闭在线客服" class="btnCtn" id="aFloatTools_Hide" style="top: 20px; display: none;" href="javascript:void(0);">收缩</a>\
    //          </div>\
    //          <div class="floatR" id="divFloatToolsView" style="width: 160px; height: 265px; display: none;">\
    //              <div class="cn cl">\
    //                  <h3 class="titZx">创客中国在线客服</h3>\
    //                  <ul>\
    //                  <li style="padding:0px;"><div style="text-align:center;color:#666;font-size:12px;padding-bottom:5px;">工作日（09:00-17:00）</div></li>\
    //                  <li><span>赛事咨询</span> <a target="_blank" href="https://wpa.qq.com/msgrd?v=3&uin=2287306168&site=qq&menu=yes"><img border="0" src="https://wpa.qq.com/pa?p=2:2287306168:51" alt="点击这里给我发消息" title="点击这里给我发消息"/></a> </li>\
    //          <li><span>技术支持</span> <a target="_blank" href="https://wpa.qq.com/msgrd?v=3&uin=793920863&site=qq&menu=yes"><img border="0" src="https://wpa.qq.com/pa?p=2:793920863:51" alt="点击这里给我发消息" title="点击这里给我发消息"/></a> </li>\
    //          <li><span>大赛报名审核咨询：<br/>86229586-6202<br/>平台与赛事合作咨询：<br/>010-68200372</span></li>\
    //          <li style="border: currentColor; border-image: none;text-align:center;"><a style="font-size:16px;display:block;color:#00bfff;text-decoration:underline" target="_blank" href="https://mp.weixin.qq.com/s?__biz=MzI1MjU2NTIxNQ==&mid=2247484178&idx=1&sn=176966473318ee867ba6510deeb1ff22&chksm=e9e080a2de9709b46a01d39773bcb3e9001a501acedae4243945ecca826f4bfe59ae04bc6376&mpshare=1&scene=1&srcid=0706GxnPSoKNUAaTe4IMBFYH#rd">常见问题(Q&A)</a></li>\
    //          </ul>\
    //      </div>\
    //  </div>\
    //</div>');
    $("#aFloatTools_Show").click(function() {
        $('#divFloatToolsView').animate({
            width: 'show',
            opacity: 'show'
        }, 100, function() {
            $('#divFloatToolsView').show();
        });
        $('#aFloatTools_Show').hide();
        $('#aFloatTools_Hide').show();
    });
    $("#aFloatTools_Hide").click(function() {
        $('#divFloatToolsView').animate({
            width: 'hide',
            opacity: 'hide'
        }, 100, function() {
            $('#divFloatToolsView').hide();
        });
        $('#aFloatTools_Show').show();
        $('#aFloatTools_Hide').hide();
    });
});
var __GlobalMunicipality = ["深圳", "厦门", "大连", "青岛", "宁波"];
var __CollegeArry = [{
    id: '1',
    name: '北京航空航天大学'
},
    {
        id: '2',
        name: '北京理工大学'
    },
    {
        id: '3',
        name: '哈尔滨工业大学'
    },
    {
        id: '4',
        name: '西北工业大学'
    },
    {
        id: '5',
        name: '哈尔滨工程大学'
    },
    {
        id: '6',
        name: '南京航空航天大学'
    },
    {
        id: '7',
        name: '南京理工大学'
    }
];
var menulist = [

    {
        text: "大赛管理",
        id: "1",
        state: 'closed',
        children: [{
            text: "首页",
            id: "101"
        },
            {
                text: "参赛项目审核",
                id: "102"
            },
            {
                text: "确认删除项目",
                id: "103"
            },
            {
                text: "地方项目评审",
                id: "104"
            },
            {
                text: "大赛初审项目",
                id: "105"
            },
            {
                text: "大赛现场赛项目",
                id: "106"
            },
            {
                text: "比赛特评",
                id: "107"
            },
            {
                text: "项目生命周期统计",
                id: "108"
            },
            {
                text: "评审项目一栏",
                id: "109"
            },
            {
                text: "大赛项目打分一览",
                id: "110"
            },
            {
                text: "现场赛打分统计",
                id: "111"
            },
            {
                text: "用户项目统计",
                id: "112"
            },
            {
                text: "区域项目统计",
                id: "113"
            },
            {
                text: "专题项目统计",
                id: "114"
            },
            {
                text: "项目投票管理",
                id: "115"
            },
            {
                text: "大赛门票管理",
                id: "116"
            },
            {
                text: "项目发布列表",
                id: "117"
            },
            {
                text: "赛区管理",
                id: "118"
            },
            {
                text: "赛事维护",
                id: "119"
            },
            {
                text: "设置PC端首页赛事",
                id: "120"
            },
            {
                text: "设置手机端首页赛事",
                id: "121"
            },
            {
                text: "设置赛事图片",
                id: "123"
            },
            {
                text: "直播维护",
                id: "124"
            },
            {
                text: "企业赛事管理",
                id: "124"
            },
            {
                text: "大赛申报",
                id: "126"
            },
            {
                text: "工业设计大奖项目审核",
                id: "127"
            },
            {
                text: "各省市申报书项目统计",
                id: "128"
            },
            {
                text: "参赛项目查看",
                id: "129"
            },
        ]
    },
    {
        text: "内容管理",
        id: "2",
        state: 'closed',
        children: [{
            text: "首页图片管理",
            id: "201"
        },
            {
                text: "直播管理",
                id: "202"
            },
            {
                text: "新闻管理",
                id: "203"
            },
            {
                text: "用户发布审核",
                id: "204"
            },
            {
                text: "广告区管理",
                id: "205"
            },
        ]
    },
    {
        text: "众包管理",
        id: "8",
        state: 'closed',
        children: [{
            text: "众包审核",
            id: "801"
        },
            {
                text: "众包数据统计",
                id: "802"
            }
        ]
    },
    {
        text: "众筹管理",
        id: "3",
        state: 'closed',
        children: [{
            text: "项目管理",
            id: "301"
        },
            {
                text: "订单管理",
                id: "302"
            },
            {
                text: "退款单管理",
                id: "303"
            },
            {
                text: "提现管理",
                id: "304"
            },
            {
                text: "众筹统计汇总",
                id: "305"
            }
        ]
    },
    {
        text: "用户管理",
        id: "5",
        state: 'closed',
        children: [{
            text: "用户管理",
            id: "501"
        },
            {
                text: "创客空间审核",
                id: "502"
            },
            {
                text: "企业空间审核",
                id: "503"
            },
            {
                text: "专家管理",
                id: "504"
            },
            {
                text: "专家打分管理",
                id: "505"
            },
            {
                text: "专家打分数目统计",
                id: "506"
            },
            {
                text: "名片管理",
                id: "507"
            },
            {
                text: "合作伙伴管理",
                id: "508"
            },
            {
                text: "省级用户管理",
                id: "509"
            },
            {
                text: "高校用户管理",
                id: "510"
            },
            {
                text: "区域专家管理",
                id: "511"
            },

        ]
    },
    {
        text: "平台管理",
        id: "6",
        state: 'closed',
        children: [{
            text: "后台管理员",
            id: "601"
        }, ]
    }
];

function getUrlParam(paramName) {
    var url = window.location.href;
    var oRegex = new RegExp('[\?&]' + paramName + '=([^&]+)', 'i');
    var oMatch = oRegex.exec(url);
    if (oMatch && oMatch.length > 1) {
        return decodeURI(oMatch[1]);
    } else {
        return "";
    }
}

function setUrlParam(name, value) {
    var reg = new RegExp("(\\?|&)" + name + "=([^&]*)(?=&|$)");
    var r = window.location.href.match(reg);
    if (r != null) {
        window.location.href = window.location.href.replace(reg, r[1] + name + "=" + escape(value));
    } else {
        var url = window.location.href;
        if (window.location.href.indexOf("?") < 0) {
            url += "?";
        } else {
            url += "&";
        }
        url += name + "=" + escape(value);
        window.location.href = url;
    }
}

function fillYear(length, jq, all, prev) {
    var date = new Date();
    var currentYear = date.getFullYear();
    if (all) {
        jq.append("<option value=\"\">全部</option>");
    }
    if (prev) {
        for (var index = currentYear - prev; index < (currentYear + length); index++) {
            if (index == currentYear) {
                jq.append("<option value=\"" + index + "\" selected=\"selected\">" + index + "</option>");
            } else {
                jq.append("<option value=\"" + index + "\">" + index + "</option>");
            }
        }
    } else {
        for (var index = currentYear; index > (currentYear - length); index--) {
            if (index == currentYear) {
                jq.append("<option value=\"" + index + "\" selected=\"selected\">" + index + "</option>");
            } else {
                jq.append("<option value=\"" + index + "\">" + index + "</option>");
            }
        }
    }
}

function changePageStyle(url) {
    var mycss;
    if (isIE()) {
        document.createStyleSheet(url);
    } else {
        $("head").append("<link href=\"" + url + "\" rel=\"stylesheet\" type=\"text/css\" />");
    }
}

function isIE() {
    var Ka = navigator.userAgent.toLowerCase();
    var rt = Ka.indexOf("opera") != -1;
    var r = Ka.indexOf("msie") != -1 && (document.all && !rt);
    return r;
}
//替换DSFA后台关键字
function replaceDSFAKeyWord(str) {
    var reg = /({)([@#&~%$][^\\}]+)}/g;
    str = str.replace(reg, function() {
        var args = arguments;
        return "\\" + args[1] + "\\" + args[2] + "}";
    });
    return str;
}

//加载样式内容
function loadStyle(styleText) {
    var s = document.createElement("style");
    s.type = "text/css";
    try { //IE
        s.styleSheet.cssText = styleText;
    } catch (e) { //FF Chrome
        s.appendChild(document.createTextNode(styleText));
    }
    document.getElementsByTagName("head")[0].appendChild(s);
}

//加载样式文件
function loadStyleFile(url) {
    var s = document.createElement("link");
    s.href = url;
    s.type = "text/css";
    s.rel = "stylesheet";
    document.getElementsByTagName("head")[0].appendChild(s);
}

function addAttribute(rows) {
    for (var index = 0; index < rows.length; index++) {
        var obj = new Object();
        for (var o in rows[index]) {
            obj[o] = rows[index][o];
        }
        rows[index]["attributes"] = obj;
        if ((rows[index].children != undefined) && (rows[index].children.length > 0)) {
            addAttribute(rows[index].children);
        }
    }
    return rows;
}

function convertToTreeData(data, idField, nameField, childrenField, boundCallback, curentLevel, levelLimit, parent) {
    levelLimit = levelLimit >= 0 ? levelLimit : null;
    curentLevel = curentLevel;
    if (data) {
        data = $.isArray(data) ? data : [data];
        var nodes = [];
        for (var i = 0; i < data.length; i++) {
            var row = data[i];
            var id = idField ? row[idField] : $.newGuid();
            var node = {
                "id": id,
                "text": row[nameField],
                attributes: row
            };
            if ($.isFunction(boundCallback)) {
                if (boundCallback(node, row, parent, curentLevel) != false) {
                    nodes.push(node);
                }
            } else {
                nodes.push(node);
            }
            var mark = true;
            var level = curentLevel + 1;

            if (levelLimit != null) {
                if (level > levelLimit) {
                    mark = false;
                    var children = row[childrenField];
                    if (children && children.length > 0) {
                        node.state = "closed";
                    }
                }
            }
            if (mark) {
                var children = row[childrenField];
                if (children && children.length > 0) {
                    var childrenNodes = convertToTreeData(children, idField, nameField, childrenField, boundCallback, level, levelLimit, row);
                    if (childrenNodes) {
                        node.children = childrenNodes;
                    }
                }
            }
        }
        return nodes;
    }
    return null;
}

function disable(index) {
    $("a.easyui-linkbutton").each(function(_index) {
        if (index.indexOf(_index) != -1) {
            $(this).linkbutton('disable');
        } else {
            $(this).linkbutton('enable');
        }
    });
}

function showButton(index) {
    $("a.easyui-linkbutton").each(function(_index) {
        if (index.indexOf(_index) != -1) {
            $(this).show();
        }
    });
}

function linkButtonsDisable(buttonsName, panel) {
    panel.find("a.easyui-linkbutton").each(function() {
        var button = $(this);
        var text = button.find(".l-btn-text");
        if ($.inArray(text.text(), buttonsName) >= 0) {
            button.linkbutton('disable');
        } else {
            button.linkbutton('enable');
        }
    });
}

function linkButtonsHidden(buttonsName, panel) {
    panel.find("a.easyui-linkbutton").each(function() {
        var button = $(this);
        var text = button.find(".l-btn-text");
        if ($.inArray(text.text(), buttonsName) >= 0) {
            button.hide();
        } else {
            button.show();
        }
    });
}

function toolbarsDisable(buttonsName, datagrid) {
    var panel = datagrid ? datagrid.datagrid("getPanel") : null;
    var el = panel || $(document);
    var toolbar = el.find(".datagrid-toolbar");
    var buttons = toolbar.find(".l-btn");
    buttons.each(function(_index) {
        var button = $(this);
        var text = button.find(".l-btn-text");
        if ($.inArray(text.text(), buttonsName) >= 0) {
            button.linkbutton('disable');
        } else {
            button.linkbutton('enable');
        }
    });
}

//提交请求
function createRequest(path, content, requestformat, responseformat, options, expro, enCode) {
    requestformat = requestformat || 'JSON';
    responseformat = responseformat || 'JSON';
    content = content || '';
    options = options || {};
    var d = content;
    var b = "";
    var isCache = false;
    var isHead = true;
    if (options) {
        if (typeof(options) == "object") {
            isCache = options.isCache || false;
            isHead = options.isHead != false ? true : false;
        } else {
            isCache = true;
        }
    }
    if (isCache) {
        b = "<Cache type='MEMORY' period='6000000000000'></Cache>";
    }
    if (typeof(content) == "string" && content.indexOf("<Data>") < 0) {
        if (enCode != false) {
            if (requestformat == "JSON") {
                //alert("test");
                var data = $("<Data></Data>").text(content);
                content = data.html();
            }
            var bb = "";
        }
        d = "<Data>" + content + "</Data>";
    }

    expro = expro ? 'exinfo="' + expro + '" ' : '';
    var name = options.name || "";

    var request = '<Request ' + (name ? 'name="' + name + '"' : "") + ' action="' + path + '" request="' + requestformat + '" response="' + responseformat + '" ' + (!isHead ? 'nohead="true"' : '') + expro + '>' + b + d + '</Request>';

    if (options.base64 != false) {
        return (new Base64()).encode(request);
    } else {
        return request;
    }
}

function openConfirm(context, callback, title, win) {
    var body = $("body");
    title = title || "提示信息";
    win = win || window.self;
    win.$.messager.confirm(title, context, function(r) {
        if (r) {
            callback();
        }
    });
}

function openAlert(context, callback, title, win) {
    var body = $("body");
    title = title || "提示信息";
    win = win || window.self;
    win.$.messager.alert(title, context, "", function() {
        callback();
    });
}

//打开对话框
// width:宽度
// height:高度
// top：y轴位置
// left:x轴位置
// iconCls：图标
// title：文字
// url：地址
//dialogMaxabled:是否可以最大化
//isClose:是否显示关闭按钮
// isFrame:是否以FRAME加载
// contentHtml 对话框内容
// overflow:是否有滚动条
// buttons：按钮
// cancelButton：是否有取消按钮
// close：关闭对话框的执行事件
// dialogArgs:参数
function OpenDialog(option) {
    var w = option.width;
    var h = option.height;
    var top = option.top || 0;
    var left = option.left || 0;
    var iconCls = option.iconCls;
    var title = option.title;
    var url = option.url || "";
    var minimizable = option.minimizable || false;
    var isFrame = option.isFrame;
    var contentHtml = option.contentHtml || "";
    var overflow = option.overflow || false;
    var buttons = option.buttons || [];
    var padding = isNaN(option.padding) ? 4 : option.padding;
    var cancelButton = option.cancelButton;
    var isClose = option.isClose != false ? true : false;
    var close = option.close;
    var dialogArgs = option.dialogArgs;
    var dialogArgs2 = option.dialogArgs2;
    var dialogArgs3 = option.dialogArgs3;
    var windowLevel = option.windowLevel;
    var opener = option.opener || window.self;
    var modal = option.modal == false ? false : true;
    var resizable = option.resizable == false ? false : true;
    var maximized = option.maximized;
    var draggable = option.draggable;
    var scroll = option.scroll || "no";
    //var dialog = $("#divDialog");
    //if (dialog.length <= 0) {
    //    var win = window.self;
    //    if (windowLevel) {
    //        win = window[windowLevel];
    //    }
    var body = $("body");
    var dialog = $("<div dialog='1' style='overflow-y:" + (overflow ? "auto" : "hidden") + "' />").appendTo(body);
    //}
    if (cancelButton != false) {
        buttons.push({
            text: '取  消',
            iconCls: 'icon-cancel',
            handler: function() {
                dialog.dialog("close");
            }
        });
    }
    var options = {
        title: title,
        iconCls: iconCls,
        width: w,
        height: h,
        modal: modal,
        inline: true,
        //border:false,
        resizable: resizable,
        maximizable: minimizable,
        maximized: maximized,
        draggable: draggable,
        closable: isClose,
        overflow: overflow,
        shadow: false,
        "onMove": function(left, top) {
            var l = left,
                t = top;
            var p = dialog.dialog("panel");
            //console.log("b")
            var mark = false;
            if (left < 0) {
                mark = true;
                l = 0;
            } else if ((left + p.outerWidth()) > $(window).width()) {}
            if (top < 0) {
                mark = true;
                t = 0;
            } else if ((top + p.outerHeight()) > $(window).height()) {}
            if (mark) {
                dialog.dialog("move", {
                    left: l,
                    top: t
                });
                return;
            }
        },
        onBeforeOpen: function() {
            var content = dialog.find(".dialog-content");
            if (!isFrame) {
                if (url != "") {
                    content.load(url);
                    dialog.data("args", dialogArgs);
                } else if (contentHtml != "") {
                    content.html(contentHtml);
                }
            } else {
                content.html("");
                var frame = $("<iframe frameborder='0' scrolling='" + scroll + "' width='100%' height='100%' src='" + url + "'></iframe>").appendTo(content);
                //frame.data("dialogArgs", dialogArgs);
                frame.get(0).dialogArgs = dialogArgs;
                frame.get(0).dialogArgs2 = dialogArgs2;
                frame.get(0).dialogArgs3 = dialogArgs3;
                frame.get(0).closeDialog = function() {
                    dialog.dialog("close")
                };
                frame.get(0).opener = opener;
                var win = frame.get(0).contentWindow;
                if (win) {
                    try {
                        win.dialogArgs = dialogArgs;
                    } catch (ex) {}
                }
            }
        },
        onOpen: function() {
            if ($.isFunction(option.open)) {
                option.open();
            }
        },
        onBeforeClose: function() {
            var content = dialog.find(".dialog-content");
            if ($.isFunction(option.close)) {
                option.close();
            }
            content.html("");
        },
        onClose: function() {
            dialog.dialog("destroy");
        }
    }
    if (option.top) {
        options.top = option.top;
    }
    if (option.left) {
        options.left = option.left;
    }
    if (buttons.length > 0) {
        options.buttons = buttons;
    } else {
        options.buttons = null;
    }
    dialog.dialog(options);
    return dialog;
}

function CloseDialog(obj) {
    var dialog = null
    if (obj.hasClass("l-btn")) {
        var el = obj.parent();
        while (el.length > 0) {
            if (el.attr("dialog") == "1") {
                dialog = el;
                break;
            } else {
                el = el.parent();
            }
        }
    } else if (el.attr("dialog") == "1") {
        dialog = obj;
    }
    dialog.dialog("close");
}

//写入调试日志
function writeLog() {
    if (window.console && console.log) {
        var args = Array.prototype.slice.call(arguments);
        console.log(args);
    }
}

function postRequestGroup(requestStr, async, callback, responseFormat, requestFormat) {
    var data = null;
    async = async || false;
    requestFormat = requestFormat || "JSON";
    responseFormat = responseFormat || "JSON";
    $.ajax({
        url: __GlobalInfo.postUrl,
        dataType: "json",
        type: "POST",
        async: async,
        data: requestStr,
        success: function(response) {
            var result = {} // response.Result
            for (var k in response) {
                if (response[k].Result.Success) {
                    result[k] = response[k].Result.Data;
                }
            }
            if (callback) {
                callback(result);
            }
            data = result;
        },
        error: function(xmlhttp) {
            //alert("格式错误")
        }
    });
    return data;
}
//读取服务器数据
function getServerJson(obj, url, async, callback, requestFormat, responseFormat, options, expro, enCode) {
    var data = null,
        error = null;
    async = async || false;
    $.ajax({
        url: url.replace("actions", "data"),
        dataType: "json",
        type: "GET",
        async: async,
        data: obj,
        success: function(response) {
            var result = null;
            if (responseFormat == "FORMAT") {
                data = response;
            } else {
                result = response;
                if (result.Success) {
                    if (callback) {
                        callback(result.Data);
                    }
                    data = result.Data;
                } else {
                    alert(result.Data);
                    error = result.Data;
                }
            }
        },
        error: function(xmlhttp) {
            error = "请求出错";
        }
    });
    if (error) {
        throw error;
    } else {
        return data;
    }
}
//读取服务器数据
function getServerData(obj, url, async, callback, requestFormat, responseFormat, options, expro, enCode) {
    // var json = getDynamicServerData({actionXml:url},'staticReq/getStaticRequest.xml');
    // if(json.result[0]!=''){
    //   return json.result[0].Data;
    // }else{
    debugger;
    var res = JSON.parse(JSON.stringify(obj));
    console.log("打印次数！")
    console.log(res)
    var name = "page_size";
    if (hasKey(res, name)) {
        var str = res.page_size.toString();
        if( str.slice(-1)=="'"){
            return;
        }
    }
    return getDynamicServerData(obj, url, async, callback, requestFormat, responseFormat, options, expro, enCode);
    //}
}

function hasKey(jsonObj, key) {
    return jsonObj.hasOwnProperty(key);
}


//动态读取服务器数据
function getDynamicServerData(obj, url, async, callback, requestFormat, responseFormat, options, expro, enCode) {
    async = async || false;
    var context = obj;
    requestFormat = requestFormat || "JSON";
    responseFormat = responseFormat || "JSON";
    if (requestFormat.toLowerCase() == "json" && obj) {
        context = JSON.stringify(obj);
    }
    var requestStr = createRequest(url, context, requestFormat, responseFormat, options, expro, enCode);
    var method = "";
    var lastIndex = url.lastIndexOf(".");
    if (lastIndex > 0) {
        var lastName = url.substr(lastIndex);
        if (lastName == ".xml" || lastName == ".bl") {
            method = "post";
        } else {
            method = "action";
        }
    } else {
        method = "post";
    }
    var ajaxUrl = method.toLowerCase() == "post" ? __GlobalInfo.postUrl : __GlobalInfo.actionUrl;

    var data = null,
        error = null;
    $.ajax({
        url: ajaxUrl,
        dataType: "json",
        type: "POST",
        async: async,
        data: requestStr,
        success: function(response) {
            var result = null;
            if (responseFormat == "FORMAT") {
                data = response;
            } else {
                result = response.Result;
                if (result.Success) {
                    if (callback) {
                        callback(result.Data);
                    }
                    data = result.Data;
                } else {
                    alert(result.Data);
                    error = "语法错误";
                }
            }
        },
        error: function(xmlhttp) {
            error = "请求出错";
        }
    });
    if (error) {
        throw error;
    } else {
        return data;
    }
}

//提交数据到服务器
function postServer(obj, url, async, requestFormat, responseFormat) {
    async = async || false;
    var context = obj;
    requestFormat = requestFormat || "JSON";
    responseFormat = responseFormat || "JSON";
    if (requestFormat.toLowerCase() == "json" && obj) {
        context = JSON.stringify(obj);
    }
    var requestStr = createRequest(url, context, requestFormat, responseFormat);
    var success = false;
    $.ajax({
        url: __GlobalInfo.postUrl,
        dataType: "json",
        type: "POST",
        async: async,
        data: requestStr,
        success: function(response) {
            var result = response.Result;
            if (result.Success) {
                success = true;
            } else {
                alert(result.Data);
                success = false;
            }
        },
        error: function(xmlhttp) {
            success = false;
        }
    });
    return success;
}

//提交并返回数据
function postReturnData(obj, url, requestFormat, responseFormat) {
    var async = false;
    var context = obj;
    requestFormat = requestFormat || "JSON";
    responseFormat = responseFormat || "JSON";
    if (requestFormat.toLowerCase() == "json" && obj) {
        context = JSON.stringify(obj);
    }
    var requestStr = createRequest(url, context, requestFormat, responseFormat);
    var data = null;
    $.ajax({
        url: __GlobalInfo.postUrl,
        dataType: "json",
        type: "POST",
        async: async,
        data: requestStr,
        success: function(response) {
            var result = response.Result;
            if (result.Success) {
                if (result.Data) {
                    data = result.Data;
                } else {
                    data = result.Success;
                }
            } else {
                alert("出现错误");
            }
        },
        error: function(xmlhttp) {}
    });
    return data;
}

//提交并返回数据异步
function postReturnDataSync(obj, url, _callback, requestFormat, responseFormat) {
    var async = true;
    var context = obj;
    requestFormat = requestFormat || "JSON";
    responseFormat = responseFormat || "JSON";
    if (requestFormat.toLowerCase() == "json" && obj) {
        context = JSON.stringify(obj);
    }
    var requestStr = createRequest(url, context, requestFormat, responseFormat);
    var data = null;
    $.ajax({
        url: __GlobalInfo.postUrl,
        dataType: "json",
        type: "POST",
        async: async,
        data: requestStr,
        success: function(response) {
            var result = response.Result;
            if (result.Success) {
                if (result.Data) {
                    data = result.Data;
                } else {
                    data = result.Success;
                }
                _callback(data);
            } else {
                alert("出现错误");
            }
        },
        error: function(xmlhttp) {}
    });
}

//解析数据
function analysisData(data, isFilterEmpty) {
    var getSplit = function(rows) {
        var number = [0, 0, 0];
        var splits = ["\t", ",", " "];
        for (var index = 0; index < 10; index++) {
            if (index >= rows.length) {
                break;
            }
            var d = $.trim(rows[index]);
            if (d != "") {
                for (var num in splits) {
                    if (d.indexOf(splits[num]) > -1) {
                        number[num] = number[num] + 1;
                    }
                }
            }
        }
        var num = 0;
        for (var index = 0; index < number.length - 1; index++) {
            if (number[index] < number[index + 1]) {
                num = (index + 1);
            }
        }
        return splits[num];
    };
    var rows = [];
    if (data.length == 0) {
        return rows;
    }
    //获取每行数据
    var _rows = data.split('\n');
    if (_rows.length == 0) {
        return rows;
    }
    var split = getSplit(_rows);
    for (var index = 0; index < _rows.length; index++) {
        if (isFilterEmpty != false) {
            if (_rows[index] == "") {
                continue;
            }
        }
        rows.push($.trim(_rows[index]).split(split));
    }
    return rows;
}

function analyzeTableCopyData(data) {
    var rows = [];
    if (data.length == 0) {
        return rows;
    }
    //获取每行数据
    var _rows = data.split('\n');
    if (_rows.length == 0) {
        return rows;
    }
    for (var i = 0; i < _rows.length; i++) {
        if (_rows[i] == "") {
            continue;
        }
        var reg = /\s|\t|,/g;
        var d = _rows[i].split(reg);
        rows.push(d);
    }
    return rows;
}

function layoutResize(layout) {
    layout = layout || $("body");
    $("body").layout("resize");
}

function layoutChildResize(layout, region, el) {
    var el = !$.isArray(el) ? [el] : el;
    var panel = layout.layout("panel", region);
    panel.panel({
        "onResize": function() {
            for (var i = 0; i < el.length; i++) {
                var e = el[i];
                e.width(panel.innerWidth()).height(panel.innerHeight());
                if ($.browser.msie && ($.browser.version == "6.0" || $.browser.version == "7.0")) {
                    if (e.get(0).id) {
                        var win = document.frames[e.get(0).id];
                        if (win) {
                            if (win.layoutResize) {
                                win.layoutResize();
                            }
                        }
                    }
                }
            }
        }
    });
    layout.layout("resize");
}

//过滤TREE数据
function filterTree(node, callback, pnode, folderMatch) {
    var n = $.extend(true, {}, node);
    var children = node.children;
    if (children && children.length > 0) {
        var mark = false;
        n.children = [];
        if (callback) {
            mark = callback(n, pnode);
        }
        if (mark) {
            if (folderMatch) {
                n.children = children;
            } else {
                for (var i = 0; i < children.length; i++) {
                    var v = children[i];
                    var result = filterTree(v, callback, node, folderMatch);
                    if (result) {
                        n.children = n.children || [];
                        n.children.push(result);
                        mark = true;
                    }
                }
            }
        } else {
            for (var i = 0; i < children.length; i++) {
                var v = children[i];
                var result = filterTree(v, callback, node, folderMatch);
                if (result) {
                    n.children = n.children || [];
                    n.children.push(result);
                    mark = true;
                }
            }
        }
        if (mark) {
            return n;
        }
    } else {
        if (callback) {
            if (callback(n, pnode)) {
                return n;
            }
        }
    }
}

//检索树结构数据
function queryTreeData(text, node, tree) {
    var n = $.extend(true, {}, node);
    if (n.text.indexOf(text) >= 0) {
        return n;
    } else {
        n.children = [];
        var children = node.children;
        var mark = false;
        if (children && children.length > 0) {
            for (var i = 0; i < children.length; i++) {
                var v = children[i];
                var result = queryTreeData(text, v, n, tree);
                if (result) {
                    n.children.push(result);
                    mark = true;
                }
            }
        }
        if (mark) {
            return n;
        } else {
            return null;
        }
    }
}

//清空所有树控件节点选中状态
function allTreeNodeUnChecked(tree) {
    var root = tree.tree("getRoots");
    $.loop(root, function(v, i) {
        tree.tree("uncheck", v.target);
        var nodes = tree.tree("getChildren", v.target);
        $.loop(nodes, function(v, i) {
            if (v.checked) {
                tree.tree("uncheck", v.target);
            }
        });
    });
}

//执行FRAME中的方法
function execFrameFunction(frame, fnname, args) {
    if (frame instanceof jQuery || frame.jquery) {
        frame = frame.get(0);
    }
    var win = frame.contentWindow;
    if ($.isFunction(win[fnname])) {
        args = args || [];
        args = $.isArray(args) ? args : [args];
        return win[fnname].apply(null, args);
    }
}

Date.prototype.format = function(format) {
    var o = {
        "M+": this.getMonth() + 1, //month
        "d+": this.getDate(), //day
        "h+": this.getHours(), //hour
        "m+": this.getMinutes(), //minute
        "s+": this.getSeconds(), //second
        "q+": Math.floor((this.getMonth() + 3) / 3), //quarter
        "S": this.getMilliseconds() //millisecond
    }

    if (/(y+)/.test(format)) {
        format = format.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    }

    for (var k in o) {
        if (new RegExp("(" + k + ")").test(format)) {
            format = format.replace(RegExp.$1, RegExp.$1.length == 1 ? o[k] : ("00" + o[k]).substr(("" + o[k]).length));
        }
    }
    return format;
}

Date.prototype.isValid = function(year, month, day) {
    var mdays = new Array(31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
    if ((year == "") || (month == "") || (day == "")) {
        return false;
    }
    if (isNaN(year) || isNaN(month) || isNaN(day)) {
        return false;
    }
    if (parseInt(month) > 12 || parseInt(month) < 1) {
        return false;
    }
    if (parseInt(day) < 1 || parseInt(day) > mdays[month - 1]) {
        return false;
    }
    //是否是闰年
    if (!(((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0))) {
        if ((month == 2) && (day > 28)) {
            return false;
        }
    }
    return true;
}

Date.prototype.getMonthWeek = function() {
    var offset = this.getDay();
    if (offset == 0) {
        offset = -6;
    } else {
        offset = (offset - 1) * -1;
    }
    sd = new Date(this.getFullYear(), this.getMonth(), this.getDate() + offset);
    ed = new Date(sd.getFullYear(), sd.getMonth(), sd.getDate() + 6);
    return Math.ceil(parseInt(ed.format("dd")) / 7);
};

String.prototype.endWith = function(s) {
    if (s == null || s == "" || this.length == 0 || s.length > this.length)
        return false;
    if (this.substring(this.length - s.length) == s)
        return true;
    else
        return false;
    return true;
}

String.prototype.startWith = function(s) {
    if (s == null || s == "" || this.length == 0 || s.length > this.length)
        return false;
    if (this.substr(0, s.length) == s)
        return true;
    else
        return false;
    return true;
}

String.prototype.formatForXml = function() {
    return this.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;");
}

$.formatForXml = function(params) {
    if (typeof(params) == "string") {
        params = params.formatForXml();
    } else {
        for (var key in params) {
            if (typeof(params[key]) == "string") {
                params[key] = params[key].formatForXml();
            }
        }
    }
    return params;
}

$.formatUserName = function(name) {
    return name;
    //    if (typeof (name) != "undefined" && name.length > 0) {
    //        return "*" + name.substring(1);
    //    }
    //    return "";
}

//重写toFixed方法
Number.prototype.toFixed = function(len) {
    len = len ? len : 0;
    var t = Math.pow(10, len);
    var num = this * t;
    num = Math.round(num) / t;
    num = num.toString();
    var i = num.indexOf(".");
    var l = len;
    var temp = "";
    if (i >= 0) {
        temp = num.substr(i + 1);
    } else {
        if (l > 0) {
            num += ".";
            temp = "";
        }
    }
    l = l - temp.length;
    for (var n = 0; n < l; n++) {
        num += "0";
    }
    return num;
}

//两数字相除
Number.prototype.accDiv = function(arg2) {
    var arg1 = this;
    var t1 = 0,
        t2 = 0,
        r1, r2;
    var numstr1 = scienceNum(arg1.toString());
    var numstr2 = scienceNum(arg2.toString());
    try {
        t1 = numstr1.toString().split(".")[1].length
    } catch (e) {}
    try {
        t2 = numstr2.toString().split(".")[1].length
    } catch (e) {}
    with(Math) {
        var num1 = new Number(arg1.toString());
        var num2 = new Number(arg2.toString());
        r1 = Number(arg1.toString().replace(".", ""))
        r2 = Number(arg2.toString().replace(".", ""))
        return (r1 / r2) * pow(10, t2 - t1);
    }
}
//两数字相乘
Number.prototype.accMul = function(arg2) {
    var arg1 = this;
    var m = 0
    var s1 = arg1.toString();
    var s2 = arg2.toString();
    try {
        m += s1.split(".")[1].length
    } catch (e) {}
    try {
        m += s2.split(".")[1].length
    } catch (e) {}
    return Number(s1.replace(".", "")) * Number(s2.replace(".", "")) / Math.pow(10, m)
}

function scienceNum(value) {
    var num = 0;
    if ((num = value.indexOf('E')) != -1 || (num = value.indexOf('e')) != -1) {
        var doubleStr = value.substring(0, num);
        var eStr = value.substring(num + 1, value.length);
        eStr = parseInt(eStr);
        if (eStr < 0) {
            var doubleStrList = doubleStr.split('.');
            var doubleStr1 = doubleStrList[0];
            var doubleStr2 = doubleStrList[1] || "";
            var length = Math.abs(eStr) - doubleStr1;
            var str = "";
            for (var i = 0; i < length; i++) {
                str += '0';
            }
            doubleStr = "0." + str + doubleStr;
            value = doubleStr;
        }
        //千分位
    }
    return value;
}

$.fn.serializeToObject = function() {
    var ctls = $("#form1").find("*[name]:disabled");
    ctls.removeAttr("disabled");
    var array = this.find("*[name]").serializeArray();
    ctls.attr("disabled", "disabled");
    var obj = {};
    for (var i = 0; i < array.length; i++) {
        obj[array[i].name] = array[i].value;
    }
    return obj;
}

//获取当前页码起始编号和末尾编号
$.getMinToMaxByPageNumber = function(pageNumber, pageSize) {
    var p = pageNumber - 1;
    var min = p * pageSize + 1;
    var max = min + pageSize - 1;
    return {
        "min": min,
        "max": max
    };
}

$.loadXml = function(initXmlPath) {
    var xml = "";
    $.ajax({
        "url": initXmlPath,
        "type": "GET",
        "dataType": "text",
        "async": false,
        "success": function(result) {
            xml = result;
        }
    });
    return xml;
}

var __htmlEncodeElement = null;

function htmlEnCode(text) {
    if (!__htmlEncodeElement) {
        __htmlEncodeElement = $("<DATA></DATA>");
    }
    __htmlEncodeElement.html("");
    text = text || "";
    __htmlEncodeElement.text(text);
    return __htmlEncodeElement.html();
}

function htmlDeCode(text) {
    if (!__htmlEncodeElement) {
        __htmlEncodeElement = $("<DATA></DATA>");
    }
    __htmlEncodeElement.html("");
    text = text || "";
    __htmlEncodeElement.html(text);
    return __htmlEncodeElement.text();
}

function objectToXml(obj, tagName, AttributePrefix) {
    var xml = "";
    var beginTag = "<" + tagName + "{0}>";
    var property = [];
    var innerText = "";
    for (var k in obj) {
        if (k == "text") {
            innerText = "<![CDATA[" + obj[k] + "]]>";
        } else {
            if (obj[k] && typeof(obj[k]) == "object") {
                if (obj[k].jquery || $.isFunction(obj[k])) {
                    continue;
                }
                if ($.isArray(obj[k])) {
                    for (var i = 0; i < obj[k].length; i++) {
                        xml += objectToXml(obj[k][i], k);
                    }
                } else {
                    xml += objectToXml(obj[k], k, AttributePrefix);
                }
            } else {
                var n = k;
                if (AttributePrefix) {
                    if (n.indexOf(AttributePrefix) == 0) {
                        n = n.replace(AttributePrefix, "");
                    }
                }
                property.push(n + "=\"" + (htmlEnCode(obj[k]) || "") + "\"");
            }
        }
    }
    var p = property.length > 0 ? " " + (property.join(" ")) : "";
    beginTag = beginTag.replace(/\{\d+\}/, p);
    var endTag = "</" + tagName + ">";
    xml = beginTag + innerText + xml + endTag;
    return xml;
}

function xmlToObject(xml, AttributePrefix) {
    //xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + xml;
    var obj = {};
    var xmldoc = $.parseXML(xml);
    xmldoc = $(xmldoc);
    var root = xmldoc.children();
    var rootName = "";
    for (var i = 0; i < root.length; i++) {
        var n = root[i];
        rootName = n.tagName;
        fn(n, obj);
    }

    function fn(node, curObject) {
        if (node.nodeType == 8) {
            return;
        }
        var tag = node.tagName;
        var nobj = null;
        if (!curObject[tag]) {
            curObject[tag] = nobj = {};
        } else {
            if (!$.isArray(curObject[tag])) {
                curObject[tag] = [curObject[tag]];
            }
            nobj = {};
            curObject[tag].push(nobj);
        }
        var attributes = node.attributes;
        for (var i = 0; i < attributes.length; i++) {
            var attr = attributes[i];
            var name = AttributePrefix ? AttributePrefix + attr.name : attr.name;
            var value = attr.nodeValue;
            if (attr.nodeValue == "false") {
                value = false;
            } else if (attr.nodeValue == "true") {
                value = true;
            } else {
                value = attr.nodeValue;
            }
            nobj[attr.name] = value;
        }
        if (node.hasChildNodes()) {
            var children = node.childNodes;
            for (var i = 0; i < children.length; i++) {
                var c = children[i];
                if (c.nodeType == 3) {
                    nobj.text = $.trim(c.wholeText || c.text || c.nodeValue);
                } else if (c.nodeType == 4) {
                    nobj.text = $.trim(c.wholeText || c.text || c.nodeValue);
                } else {
                    fn(c, nobj);
                }
            }
        }
    }
    return obj[rootName];
}

function getXmlObj(path) {
    var resultObj = {};
    $.ajax({
        url: __GlobalInfo.webroot + "/" + path,
        data: {
            time: new Date().getTime()
        },
        dataType: "text",
        type: "POST",
        async: false,
        success: function(result) {
            if (result) {
                resultObj = xmlToObject(result);
            }
        },
        "error": function(result) {
            alert(result);
        }
    })
    return resultObj;
}

function arithmetic(arg1, operator, arg2) {
    var r1, r2, n, mul, size;
    try {
        r1 = arg1.toString().split(".")[1].length;
    } catch (e) {
        r1 = 0;
    }
    try {
        r2 = arg2.toString().split(".")[1].length;
    } catch (e) {
        r2 = 0;
    }
    size = Math.max(r1, r2);
    switch (operator) {
        case "+":
        case "-":
            mul = size;
            break;
        case "*":
            mul = 2 * size;
            break;
        case "/":
            mul = 0;
            break;
    }
    //动态控制精度长度
    n = (r1 >= r2) ? r1 : r2;
    return (eval((arg1 * Math.pow(10, size)) + operator + (arg2 * Math.pow(10, size))) / Math.pow(10, mul)).toFixed(n);
}

//获取SQLWHERE 条件
function createWhereSqlPart(item) {
    function getValue(item) {
        var operator = item.operator;
        var s = "";
        var vs = [];
        var itemvalue = $.isArray(item.value) ? item.value : [item.value];
        if (item.attributes.type == "数字") {
            $.loop(itemvalue, function(v, i) {
                vs.push(v);
            });
        } else if (item.attributes.type == "日期") {
            $.loop(itemvalue, function(v, i) {
                vs.push("TO_DATE('" + v + "','yyyy-mm-dd')");
            });
        } else {
            $.loop(itemvalue, function(v, i) {
                vs.push("'" + v + "'");
            });
        }
        if (operator == "IN" || operator == "NOT IN") {
            s = item.attributes.table.alias + "." + item.attributes.fieldName + " " + item.operator + " (" + vs.join(",") + ")";
        } else if (operator == "IS" || operator == "IS NOT") {
            s = item.attributes.table.alias + "." + item.attributes.fieldName + " " + item.operator + "NULL";
        } else if (operator == "BETWEEN") {
            s = item.attributes.table.alias + "." + item.attributes.fieldName + " " + item.operator + " " + vs.join(" AND ");
        } else if (operator == "LIKE") {
            s = item.attributes.table.alias + "." + item.attributes.fieldName + " " + item.operator + " '%'||" + vs.join() + "||'%'";
        } else {
            s = item.attributes.table.alias + "." + item.attributes.fieldName + item.operator + vs.join();
        }
        return s;
    }
    return getValue(item);
}

function initEasyUiValidatebox() {
    $.extend($.fn.validatebox.defaults.rules, {
        indicatorcode: {
            // 省份证号和市民卡号混合验证
            validator: function(value) {
                if (value.length != 6) {
                    return false;
                } else {
                    return /^[0-9]+$/i.test(value);
                }
            },
            message: '编码长度不正确'
        }
    });
}

/**
 * 获取资源文件常量配制信息 参数名必须全部大写字每，比如 (TJZD)统计制度模块
 * @param moduleName
 */
function getResource(moduleName) {
    var resultObj = getXmlObj("config/dsf.xml");
    var webName = null;
    if (resultObj.Application.ApplicationName) {
        webName = resultObj.Application.ApplicationName.value;
    } else {
        webName = "DefaultResource";
    }
    var resources = getXmlObj("config/resource.xml");
    var resource = null;
    if (resources[webName] && resources[webName][moduleName]) {
        resource = resources[webName][moduleName];
    } else {
        resource = resources["DefaultResource"][moduleName];
    }
    return resource;
}

/**
 * 获取当前服务器时间
 * @param format 参数为空默认返回当前毫秒值
 */
function getServerTime(format) {
    if (!format) {
        format = "";
    }
    var result = getServerData({
        FORMAT: format
    }, "home/actions/javagetservertime.xml");
    return result.TIME;
}

function fillSelect(jq, data, keyfield, valuefield) {
    keyfield = keyfield || 'id';
    valuefield = valuefield || 'text';
    $.each(data, function(i, v) {
        jq.append("<option value='" + v[keyfield] + "'>" + v[valuefield] + "</option>");
    });
}

function Base64() {

    // private property
    _keyStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=";

    // public method for encoding
    this.encode = function(input) {
        if (input == null) return null;

        var output = "";
        var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
        var i = 0;
        input = _utf8_encode(input);
        while (i < input.length) {
            chr1 = input.charCodeAt(i++);
            chr2 = input.charCodeAt(i++);
            chr3 = input.charCodeAt(i++);
            enc1 = chr1 >> 2;
            enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
            enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
            enc4 = chr3 & 63;
            if (isNaN(chr2)) {
                enc3 = enc4 = 64;
            } else if (isNaN(chr3)) {
                enc4 = 64;
            }
            output = output +
                _keyStr.charAt(enc1) + _keyStr.charAt(enc2) +
                _keyStr.charAt(enc3) + _keyStr.charAt(enc4);
        }
        return output;
    }

    // public method for decoding
    this.decode = function(input) {
        if (input == null) return null;
        var output = "";
        var chr1, chr2, chr3;
        var enc1, enc2, enc3, enc4;
        var i = 0;
        input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
        while (i < input.length) {
            enc1 = _keyStr.indexOf(input.charAt(i++));
            enc2 = _keyStr.indexOf(input.charAt(i++));
            enc3 = _keyStr.indexOf(input.charAt(i++));
            enc4 = _keyStr.indexOf(input.charAt(i++));
            chr1 = (enc1 << 2) | (enc2 >> 4);
            chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
            chr3 = ((enc3 & 3) << 6) | enc4;
            output = output + String.fromCharCode(chr1);
            if (enc3 != 64) {
                output = output + String.fromCharCode(chr2);
            }
            if (enc4 != 64) {
                output = output + String.fromCharCode(chr3);
            }
        }
        output = _utf8_decode(output);
        return output;
    }

    // private method for UTF-8 encoding
    _utf8_encode = function(string) {
        string = string.replace(/\r\n/g, "\n");
        var utftext = "";
        for (var n = 0; n < string.length; n++) {
            var c = string.charCodeAt(n);
            if (c < 128) {
                utftext += String.fromCharCode(c);
            } else if ((c > 127) && (c < 2048)) {
                utftext += String.fromCharCode((c >> 6) | 192);
                utftext += String.fromCharCode((c & 63) | 128);
            } else {
                utftext += String.fromCharCode((c >> 12) | 224);
                utftext += String.fromCharCode(((c >> 6) & 63) | 128);
                utftext += String.fromCharCode((c & 63) | 128);
            }

        }
        return utftext;
    }

    // private method for UTF-8 decoding
    _utf8_decode = function(utftext) {
        var string = "";
        var i = 0;
        var c = c1 = c2 = 0;
        while (i < utftext.length) {
            c = utftext.charCodeAt(i);
            if (c < 128) {
                string += String.fromCharCode(c);
                i++;
            } else if ((c > 191) && (c < 224)) {
                c2 = utftext.charCodeAt(i + 1);
                string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
                i += 2;
            } else {
                c2 = utftext.charCodeAt(i + 1);
                c3 = utftext.charCodeAt(i + 2);
                string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
                i += 3;
            }
        }
        return string;
    }
}

/***用户验证***/
function ValueUserInfo(type, url,id) {
    var currentUrl = window.location.href;
    var g_userid = $.sessionHelper.getSession(["userid"]).userid;
    if (!g_userid || g_userid == "") {
        window.location.href = __GlobalInfo.webroot + "/register/choiceStatus.html";
        return;
    } else {
        var result = getServerData({id: id,  make:"get_match"  }, "admin_new/controller/manage/match_operate.xml");
        if(result && result.match && result.match.outlink){
            window.location.href = result.match.outlink;
        }else{
            var str =   "?comp_id="+id
            window.location.href = __GlobalInfo.webroot + "/zone/company_publish.html"+str;
        }
    }
    //var gl_certification = $.sessionHelper.getSession(["certification"]).certification;
    //// work 作评提交 attend 应征任务  project 发布众筹   demand 众包
    //if (type == "work" || type == "attend") {
    //    //发布任务可以不用传url 
    //    if (type == "work" && !url) {
    //        url = encodeURIComponent(__GlobalInfo.webroot + "/zone/workscommit.html");
    //    }
    //    var _identity_ = {};
    //    var data = getServerData({}, "zone/actions/initWorksControlData2.xml");
    //    if (data.userallinfo) {
    //        _nowusertype = data.userallinfo.USER_TYPE;
    //        switch (_nowusertype) {
    //            case "8"://个人
    //                _identity_.identity_name = data.userallinfo.USER_NAME;
    //                _identity_.identity_province = data.userallinfo.PROVINCE;
    //                _identity_.identity_city = data.userallinfo.CITY;
    //                _identity_.identity_dlist = data.userallinfo.DLIST;
    //                _identity_.identity_address = data.userallinfo.ADDRESS;
    //                break;
    //            case "9"://创客空间
    //                _identity_.identity_name = data.userallinfo.MAKER_NAME;
    //                _identity_.identity_province = data.userallinfo.PROVINCE_D;
    //                _identity_.identity_city = data.userallinfo.CITY_D;
    //                _identity_.identity_dlist = data.userallinfo.DLIST_D;
    //                _identity_.identity_address = data.userallinfo.ADDRESS_D;
    //                break;
    //            case "10"://企业
    //                _identity_.identity_name = data.userallinfo.COMPANY_NAME;
    //                _identity_.identity_province = data.userallinfo.PROVINCE_C;
    //                _identity_.identity_city = data.userallinfo.CITY_C;
    //                _identity_.identity_dlist = data.userallinfo.DLIST_C;
    //                _identity_.identity_address = data.userallinfo.ADDRESS_C;
    //                break;
    //            case "13"://合作伙伴
    //                _identity_.identity_name = data.userallinfo.USER_NAME;
    //                _identity_.identity_province = data.userallinfo.PROVINCE;
    //                _identity_.identity_city = data.userallinfo.CITY;
    //                _identity_.identity_dlist = data.userallinfo.DLIST;
    //                _identity_.identity_address = data.userallinfo.ADDRESS;
    //                break;
    //        }
    //        _identity_.identity_hyname = data.userallinfo.HYNAME;
    //        _identity_.identity_special_name = data.userallinfo.SPECIAL_NAME;
    //        _identity_.identity_hycode = data.userallinfo.HYCODE;
    //        _identity_.identity_special_id = data.userallinfo.SPECIAL_ID;

    //        if ((!_identity_.identity_province || !_identity_.identity_hycode || !_identity_.identity_special_id) && _nowusertype != "13") {
    //            alert("请先完善项目身份(所在地区、专注行业、专题领域)。");
    //            switch (_nowusertype) {
    //                case "8"://个人

    //                    window.location.href = __GlobalInfo.webroot + "/account/userinfo.html?url=" + url;
    //                    break;
    //                case "9"://创客空间
    //                    window.location.href = __GlobalInfo.webroot + "/account/spaceinfo.html?url=" + url;
    //                    break;
    //                case "10"://企业
    //                    window.location.href = __GlobalInfo.webroot + "/account/companyinfo.html?url=" + url;
    //                    break;
    //                case "13"://合作伙伴
    //                    window.location.href = __GlobalInfo.webroot + "/account/hzhb_compeinfo.html?url=" + url;
    //                    break;
    //                default:
    //                    window.location.href = __GlobalInfo.webroot + "/";
    //                    break;
    //            }
    //            return;
    //        } else if (_nowusertype == "13") {
    //            if (!_identity_.identity_province && !_identity_.identity_hycode && !_identity_.identity_special_id) {
    //                alert("请先完善项目身份(所在地区、专注行业、专题领域)。");
    //                window.location.href = __GlobalInfo.webroot + "/account/hzhb_compeinfo.html?url=" + url;
    //                return;
    //            }

    //            //if (gl_certification != "1") {
    //            //    alert("还需要完成实名认证");
    //            //    window.location.href = __GlobalInfo.webroot + "/account/authentication.html?url=" + url1;
    //            //    return;
    //            //}

    //            window.location.href = decodeURIComponent(url);
    //        }

    //        //if (gl_certification != "1") {
    //        //    alert("还需要完成实名认证");
    //        //    window.location.href = __GlobalInfo.webroot + "/account/authentication.html?url=" + url;
    //        //    return;
    //        //}

    //        window.location.href = decodeURIComponent(url);

    //    } else {
    //        window.location.href = __GlobalInfo.webroot + "/login/login.html?url=" + encodeURIComponent(currentUrl);
    //        return;
    //    }
    //} else if (type == "project" || type == "demand") {
    //    if (type == "project" && !url) {
    //        url = __GlobalInfo.webroot + "/z/addproject.html";
    //    } else if (type == "demand" && !url) {
    //        url = __GlobalInfo.webroot + "/account/demandadd_bylink.html";
    //    }
    //    var g_certification = $.sessionHelper.getSession(["certification"]).certification;
    //    if (g_certification != "1") {
    //        if (type == "project") {
    //            alert("未通过实名认证！不能发起众筹。");
    //        } else {
    //            alert("未通过实名认证！不能发起众包。");
    //        }
    //        window.location.href = __GlobalInfo.webroot + "/account/authentication.html";
    //        return;
    //    } else {
    //        window.location.href = url;
    //    }
    //}
}

//获取密码强度等级
function getPassWordLevel(pwd) {
    var pwdlv = 30;
    if (pwd.length < 6) {
        pwdlv = 30;
        return;
    }
    var reg1 = /[0-9]/;
    var reg2 = /[a-zA-Z]/;
    var reg3 = /[!\*@#$%_~\?<>;,^]/;
    var t1 = reg1.test(pwd);
    var t2 = reg2.test(pwd);
    var t3 = reg3.test(pwd);
    if (t1 || t2 || t3) {
        pwdlv = 30;
    }
    if ((t1 && t2) || (t1 && t3) || (t2 && t3)) {
        pwdlv = 60;
    }
    if (t1 && t2 && t3) {
        pwdlv = 100;
    }
    return pwdlv;
}

//取参并重定向
function getSuperRedirect(inputUrl, eliminateUrl) {
    var returnUrl = inputUrl;
    var eliminate = [];
    if (eliminateUrl) {
        eliminate = eliminateUrl.split(',');
    }
    var url = location.href;
    var paramStr = url.substring(url.indexOf('?') + 1, url.length).split('&');
    var j;
    var count = 0;
    var paramObj = {};
    for (var i = 0; j = paramStr[i]; i++) {
        var key = j.substring(0, j.indexOf('=')).toLowerCase();
        var value = j.substring(j.indexOf('=') + 1, j.length);
        if ($.trim(key) != "") {
            var isInject = true;
            if (eliminate.length > 0) {
                for (var el = 0; el < eliminate.length; el++) {
                    if ($.trim(key) == eliminate[el]) {
                        isInject = false;
                    }
                }
            }
            if (isInject) {
                paramObj[key] = value;
                count++;
            }
        }
    }

    for (var k in paramObj) {
        if (returnUrl.indexOf('?') > -1) {
            returnUrl += "&" + k + "=" + paramObj[k];
        } else {
            returnUrl += "?" + k + "=" + paramObj[k];
        }
    }
    for (var i = 2; i < arguments.length; i++) {
        if (arguments[i] != undefined) {
            var _key = arguments[i].split('=')[0];
            var _value = arguments[i].split('=')[1];
            if (returnUrl.indexOf('?') > -1) {
                returnUrl += "&" + _key + "=" + _value;
            } else {
                returnUrl += "?" + _key + "=" + _value;
            }
        }
    }
    window.location.href = returnUrl;
}

/**
 * 发送消息至队列中
 * @param QueueName 队列名称
 * @param message 消息内容，如果为json格式请转换为字符串并且前面加#
 */
function sendMqInfo(QueueName, message) {
    getServerData({
        QueueName: QueueName,
        message: message
    }, "home/actions/sendMqInfo.xml", true, function() {});
}

function compeDetailsJump() {
    window.location.href = __GlobalInfo.webroot + "/ds/detail/" + cid + ".html";
}
//禁用成功转化以及融资对接页面
$(document).ready(function() {
    // 获取最后两个li元素
var liElements = document.querySelectorAll('.w_1200_header li:nth-last-child(-n+2)');

// 遍历最后两个li元素，并禁用它们以及子项的点击事件
liElements.forEach(function(liElement) {
    liElement.addEventListener('click', function(event) {
        event.stopPropagation(); // 阻止事件冒泡
        event.preventDefault(); // 阻止默认点击事件
    });

    // 禁用子项的点击事件
    var childItems = liElement.querySelectorAll('a');
    childItems.forEach(function(childItem) {
        childItem.style.cursor = 'not-allowed';
        childItem.addEventListener('click', function(event) {
            event.stopPropagation(); // 阻止事件冒泡
            event.preventDefault(); // 阻止默认点击事件
        });
    });
});
})