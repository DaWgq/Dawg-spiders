var debugflag = false;
document.onkeydown = function () {
    if ((e.ctrlKey) && (e.keyCode === 83)) {
        alert("检测到非法调试，小心我抽你");
        return false
    }
}
;
document.onkeydown = function () {
    var e = window.event || arguments[0];
    if (e.keyCode === 123) {
        alert("检测到非法调试，小菜鸡别爬了");
        return false
    }
}
;
document.oncontextmenu = function () {
    alert("检测到非法调试，小菜鸡别爬了");
    return false
}
;
// !function () {
//     if (window.outerWidth - window.innerWidth > 210 || window.outerHeight - window.innerHeight > 210) {
//         document.getElementsByTagName("body")[0].innerHTML = '检测到非法调试, 请关闭调试终端后刷新本页面重试!<br/>Welcome for People, Not Welcome for Machine!<br/>';
//         window.location.href = "about:blank";
//     }
//     let handler = setInterval(() => {
//             if (window.outerWidth - window.innerWidth > 210 || window.outerHeight - window.innerHeight > 210) {
//                 document.getElementsByTagName("body")[0].innerHTML = '检测到非法调试, 请关闭调试终端后刷新本页面重试!<br/>Welcome for People, Not Welcome for Machine!<br/>';

//                 debugflag = true
//             }
//             let before = new Date();
//             (function () {
//             }
//                 ["constructor"]("debugger")());
//             let after = new Date();
//             let cost = after.getTime() - before.getTime();
//             if (cost > 50) {
//                 debugflag = true;
//                 try {
//                     document.getElementsByTagName("body")[0].innerHTML = '检测到非法调试, 请关闭调试终端后刷新本页面重试!<br/>Welcome for People, Not Welcome for Machine!<br/>';
//                     document.write('检测到非法调试, 请关闭调试终端后刷新本页面重试!<br/>');
//                     document.write("Welcome for People, Not Welcome for Machine!<br/>")
//                 } catch (err) {
//                     alert('检测到非法调试, 请关闭调试终端后刷新本页面重试!')
//                 }
//             }
//         }
//         , 2000)
// }();


function loadPage(pageNumber) {
    // 使用全局变量 problemId
    const params = {
        page: pageNumber,
    };
    const queryString = new URLSearchParams(params).toString();
    fetch(`/api/problem-detail/${problemId}/data/?${queryString}`)
        .then(response => response.json())
        .then(data => updatePageContent(data))
        .catch(error => console.error('Error fetching problem details:', error));
}
