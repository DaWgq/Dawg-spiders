var project = new Vue({
	el: '#project',
	data() {
		return {
			login_id: $.sessionHelper.getSession(["userid"]).userid,
			tab: '',
			page_size: 12,
			page_index: 1,
			startIndex: 0,
			total: 0,
			title: "",
			currentPage:1,
			project: [],
			product_classesList: [],
			hycode: '',
		}
	},
	methods: {
		toSearchProduct() {
			this.startIndex = 0;
			this.currentPage = 1;
			this.searchProject();
			console.log("ceshi1")
		},
		initRadio() {
			this.product_classesList = getServerData({
				"make": "get_product_classes"
			}, "register/actions/register.xml").product_classes || [];
			// this.changeTab('1',this.product_classesList[0].hyname,this.product_classesList[0].hycode)
		},
		initProject() {
			var data = {
				"start_index": this.startIndex,
				"page_size": this.page_size,
				"classid": this.tab,
				"title": this.title,
				"classid": this.hycode
			};
			var xmlPath = "ds/actions/getProducts.xml";
			var result = getServerData(data, xmlPath);
			console.log(result, data, "项目列表")
			this.project = result.products;
			this.total = result.total_count*1;
		},
		searchProject() {
			var data = {
				"start_index": this.startIndex,
				"page_size": this.page_size,
				"classid": this.tab,
				"title": this.title,
				"classid": this.hycode
			};
			var xmlPath = "ds/actions/getProducts.xml";
			var result = getServerData(data, xmlPath);
			console.log(result, data, "项目列表")
			this.project = result.products;
			this.total = result.total_count*1;
		},
		changeTab(num, titlee, code) {
			this.tab = num;
			this.page_index = 1;
			this.startIndex = 0;
			this.currentPage = 0;
			this.project = []
			// this.title = titlee
			this.hycode = code
			// if (num == '1') {
			// 	this.title = "智能硬件"
			// } else if (num == '3') {
			// 	this.title = "创意设计"
			// } else if (num == '2') {
			// 	this.title = "移动应用"
			// } else if (num == '6') {
			// 	this.title = "其它"
			// } else {
			// 	this.title = ""
			// }
			this.initProject()
		},
		toDetail(id) {
			window.open('../product.html?productid=' + id, '_blank')
		},
		// 自动加载数据
		loadauto() {
			// this.loading = false;

			let scrollTop = document.documentElement.scrollTop || document.body.scrollTop;

			let clientHeight = document.documentElement.clientHeight;

			let scrollHeight = document.documentElement.scrollHeight;

			let bottomOfWindow = scrollTop + clientHeight >= scrollHeight - 4


			if (scrollTop != 0 && bottomOfWindow) {

				// this.loading = true
				if (this.total > this.page_index * this.page_size) {
					this.page_index++;
					this.startIndex = (this.page_index - 1) * this.page_size
					// console.log(this.page_index, this.startIndex, "数据")
					this.initProject()
				} else {
					console.log("没有了")
				}



			}
		},
		tiaozhuan(url) {
			window.open(url, '_blank')
		},
		// 分页
		handleSizeChange(val) {
			console.log(`每页 ${val} 条`);
			this.page_size = val;
			this.currentPage = 1;
			this.startIndex = 0;
			this.initProject()
		},
		handleCurrentChange(val) {
			console.log(`当前页: ${val}`);
			this.currentPage = val;
			this.startIndex = (this.currentPage - 1) * Number(this.page_size);
			this.initProject()
		}
	},
	mounted() {
		localStorage.setItem("target", "找项目")
		this.initRadio()
		this.initProject()
		// window.addEventListener('scroll', this.loadauto);
	}
})