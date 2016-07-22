var fs = require('fs');//引入filesystem模块。
var os = require('os');//引入os模块

//封装parse类
var parseini = {
	//正则
	"pattern" : {
		"block" : /^\[(.+)\]$/, //配置块声明
		"comment" : /^;|#/, //注释段
		"item" : /^ *(\w+) *\: *("?.+"?) *$/, //匹配配置项
		"include" : /^@include ([a-z0-9_\.\/]+)$/i, //引入文件
		"group" : /^(\w+)((\.\w+)+)$/, //配置块声明中的组声明
		"itemArr" : /^ *(\w+)\[\] *\: *("?.+"?) *$/, //配置项的组
	},
	//当前配置块
	"current" : "",
	//配置文件存放位置
	"config" : new Object(),
	//文件存放数组
	"lines" : [],
	//字符集
	"chatset" : 'utf8',
	//配置文件根路径
	"configRoot" : [],
	//系统根路径
	"systemRoot" : '/',
	//当前load文件路径
	"currentPath" :[],

	//加载文件方法
	"load" : function(file){
		//同步读取文件
		var data = fs.readFileSync(file , this.charset);
		return data.split(os.EOL); //返回行数组
	},
	//解析方法
	"parse" : function(line){
		if(this.pattern.block.test(line)){
			//配置段匹配
			var match = line.match(this.pattern.block);
			this.current = match[1]; //组配置在其他具体配置中再解析
		}else{
			//值配置区域
			if(this.pattern.group.test(this.current)){
				//组配置
				var groupArr = this.current.split('.'); //获取配置组
				var evalGroup = 'this.config';
				for(var i = 0 ; i < groupArr.length ; i++){
					evalGroup += '.' + groupArr[i];
					var evalStr = "if(typeof " + evalGroup + " == 'undefined'){ " + evalGroup + " = new Object(); }";
					eval(evalStr); //执行创建语句
				}

				//item配置
				if(this.pattern.item.test(line)){
					var match = line.match(this.pattern.item);
					var evalStrValue = "this.config." + this.current + "." + match[1] +  " = this.getRealTypeValue(match[2])";
					eval(evalStrValue); //执行赋值语句
					return;
				}

				//数组配置项
				if(this.pattern.itemArr.test(line)){
					var match = line.match(this.pattern.itemArr);
					var evalStrIf = "if(typeof this.config." + this.current + "." + match[1] + " == 'undefined'){thi.config." + this.current + "." + match[1] + " = new Array(); }";
					eval(evalStrIf); //运行创建语句
					var evalStrValue = "this.config." + this.current + "." + match[1] + ".push(this.getRealTypeValue(match[2]));";
					eval(evalStrValue); //运行赋值语句
					return;
				}

			}else{
				if(typeof this.config[this.current] == 'undefined'){
					this.config[this.current] = new Object();
				}

				//item配置
				if(this.pattern.item.test(line)){
					var match = line.match(this.pattern.item);
					this.config[this.current][match[1]] = this.getRealTypeValue(match[2]);
					return;
				}

				//数组配置项
				if(this.pattern.itemArr.test(line)){
					var match = line.match(this.pattern.itemArr);
					if(typeof this.config[this.current][match[1]] == 'undefined'){
						this.config[this.current][match[1]] = new Array();
					}
					this.config[this.current][match[1]].push(this.getRealTypeValue(match[2]));
					return;
				}
			}
		}
	},
	//引入处理方法,返回引入文件的真实路径。
	"include" : function(line , currFile){
		//切换当前路径
		this.switchCurrentPath(currFile);
		var match = line.match(this.pattern.include); //获取路径及文件名
		var filename = match[1];
		//判断路径类型
		if(!this.isRe(filename)){
			return filename; //如果是绝对路径，直接返回
		}else{
			var chi = /^\.\/(([a-z0-9_\-\.]+\/)+)([a-z0-9_\-\.]+)$/i; //./ab/ac/ad/a.ini 路径部分存在 第二个子模式(ab/ac/ad/)，文件名部分为第四个子模式(a.ini)
			var par = /^((\.\.\/)+)(([a-z0-9_\-\.]+\/)*)([a-z0-9_\-\.]+)$/i; //../../../test/a/a.ini 第二个子模式：../的匹配(../../../)，第四个子模式路径匹配(test/a/)，第六个子模式文件名匹配(a.ini)
			var fil = /^([a-z0-9_\-\.]+)$/i; //只匹配文件名
			var fil2 = /^\.\/([a-z0-9_\-\.]+)$/i;
			//判断是不是直接文件名
			if(fil.test(filename)){
				var match = filename.match(fil);
				var path = this.currentPath.join('/'); //组成路径的中间部分
				path = this.systemRoot + path + '/'; //加上跟路径 or 盘符 和 路径最后的 /
				return path + match[1]; // 路径 + 文件名 返回
			}

			//匹配./file.ini
			if(fil2.test(filename)){
				var match = filename.match(fil2);
				var path = this.currentPath.join('/'); //组成路径的中间部分
				path = this.systemRoot + path + '/'; //加上跟路径 or 盘符 和 路径最后的 /
				return path + match[1]; // 路径 + 文件名 返回
			}

			//判断是不是当前路径下的其他目录
			if(chi.test(filename)){
				var match = filename.match(chi);
				var path = this.currentPath.join('/');
				return this.systemRoot + path + '/' + match[1] + match[3];
			}

			//判断是不是当前的上级目录
			if(par.test(filename)){
				var match = filename.match(par);
				var currTmp = this.currentPath; //获取当前目录
				var dotDotSlasheStr = match[1]; //获取../字符串
				var pathStr = match[3]; //获取path 字符串
				var fileOnlyName = match[5];
				//统计../的数量。
				var dotDotSlasheNum = this.getSubNum('../' , dotDotSlasheStr);
				for(var i = 0 ; i < dotDotSlasheNum ; i++){
					if(currTmp.length < 1){
						return false; //如果目录为空，不能再次往上了，就返回false
					}
					currTmp.pop(); //弹出最后一个元素，相当于返回一级目录
				}
				//处理path
				pathStr = pathStr ? pathStr : '';
				return this.systemRoot + currTmp.join('/') + '/' + pathStr + fileOnlyName;
			}

			return false;
		}
	},
	//获取子字符串在目标字符串出现的次数
	"getSubNum" : function(search , subject){
		var num = 0;
		var i = 0;
		while(i < subject.length){
			subject = subject.substr(i);
			var tmp = subject.indexOf(search);
			if(tmp == -1){
				break;
			}else{
				num++;
				i = tmp + search.length;
			}
		}
		return num;
	},
	//判断是否是相对路径，include方法的正则有点bug
	"isRe" : function (file){
		var re1 = /^\.\//;
		var re2 = /^\.\.\//;
		var re3 = /^\w+/;
		if(re1.test(file) || re2.test(file) || re3.test(file)){
			return true;
		}else{
			return false;
		}
	},
	//切换当前路径
	"switchCurrentPath" : function(file){
		if(os.type() == 'Windows_NT'){ //处理不同操作系统
			//处理路径
			file = file.replace( /\\/g , '/' );//将windows的\转化为/
			var tmp = fileP.split('/');
			tmp.shift();//弹出头部盘符为系统根
			tmp.pop();
			this.currentPath = tmp;
		}else{
			var tmp = file.split('/');
			tmp.shift(); //弹出空
			tmp.pop();//移除文件名
			this.currentPath = tmp; //当前文件路径
		}
	},
	//获取最终的lines，处理完所有的include引入的结果。
	"finalLines" : function(file){
		var lineArr = this.load(file);
		var tmp = [];
		for(var i = 0 ; i < lineArr.length ; i++){
			if(this.pattern.include.test(lineArr[i])){ //判断是否有引入
				var includeFile = this.include(lineArr[i] , file); //获取引入文件
				if(!includeFile){
					continue; //如果文件不合法，跳过本行。
				}
				var result = this.finalLines(includeFile); //递归调用自己
				for(var j = 0 ; j < result.length ; j++){
					tmp.push(result[j]); //合并
				}
			}else{
				tmp.push(lineArr[i]);
			}
		}
		return tmp;
	},
	//处理路径
	"processPath" : function(file){
		//获得配置文件路径
		var filePath = fs.realpathSync(file);
		if(os.type() == 'Windows_NT'){ //处理不同操作系统
			//处理路径
			filePath = filePath.replace( /\\/g , '/' );//将windows的\转化为/
			var tmp = filePath.split('/');
			this.systemRoot = tmp.shift() + '/';//弹出头部盘符为系统根
			tmp.pop();
			this.configRoot = tmp;//剩下的为路径数组
			this.currentPath = tmp;
		}else{
			var tmp = filePath.split('/');
			tmp.shift(); //弹出空
			tmp.pop();
			this.systemRoot = '/';
			this.configRoot = tmp;
			this.currentPath = tmp; //当前文件路径
		}
		return filePath;
	},
	//判断类型，并返回类型。
	"getRealTypeValue" : function(value){
		var integers = /^\d+$/;
		var floats = /^\d+\.\d+$/;
		var strings = /^"(.*)"$/;
		var booleans = /^true|false$/i;

		if(strings.test(value)){
			var val = value.match(strings);
			return val[1];
		}//字符串

		if(integers.test(value)){
			return parseInt(value);
		}//整数

		if(floats.test(value)){
			return parseFloat(value);
		}//浮点数

		if(booleans.test(value)){
			var val = value.toLowerCase();
			if(val == 'false'){
				return false;
			}else{
				return true;
			}
		}//boolean值

		return value; //原样返回
	},
	//入口方法
	"getConfig" : function(file , charset){
		//默认字符集为utf8
		charset = arguments[1] ? arguments[1] : 'utf8';
		this.charset = charset;

		//处理路径
		file = this.processPath(file);
		//处理lines
		this.lines = this.finalLines(file);
		//return this.lines;//调试，看include是否正常
		for(var i = 0 ; i < this.lines.length ; i++){
			this.parse(this.lines[i]);
		}
		return this.config;
	}
}

exports.parse = parseini;
