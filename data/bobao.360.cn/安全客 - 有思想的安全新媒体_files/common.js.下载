var mynoty = {
    error: function (data) {
        noty({
            layout: 'center',
            text: data,
            type: "error",
            layout:"center",
                    theme: 'defaultTheme',
            timeout: 800,
        });
    },
    ajaxShow: function (data, callback) {
        noty({
            layout: 'center',
            text: data.msg,
            type: data.success ? "success" : "error",
            layout:"center",
                    theme: 'defaultTheme',
            timeout: 800
        });
        if (callback) {
            callback();
        }
    }
}

var _nick_name=false;
//表单选择搜索类型
var formSel = {
    types: ["漏洞", "资讯", "知识", "漏洞，资讯或知识"],
    inputEl: $("#search #type"),
    el: $(".bug"),
    selecteeWr: $(".bug .typelist"),
    selectee: [],
    showText: $(".bug .seled"),
    handleOver: function (e) {
        if (!formSel.selecteeWr.is(":animated")) {
            formSel.selecteeWr.slideDown();
        }
    },
    handleLeave: function (e) {
        formSel.selecteeWr.slideUp();
    },
    handleClick: function (e) {
        var $this = $(this);
        formSel.inputEl.val($this.data("index"));
        formSel.showText.text($this.text());
        formSel.selecteeWr.find(".hide").removeClass("hide");
        $this.addClass("hide");
        formSel.selecteeWr.slideUp();
        if ($this.data("index") != undefined) {
            $("input[name='type']").val($this.data("index"));
            $(".keys").attr("placeholder", "搜索" + formSel.types[$this.data("index")]);
        }
    },
    bind: function () {
        this.el.on("mouseover", this.handleOver);
        this.el.on("mouseleave", this.handleLeave);
        this.selecteeWr.on("click", "li", this.handleClick);
    },
    init: function () {
        this.bind();
        var val = this.inputEl.val();
        this.selectee = formSel.selecteeWr.find("li");
        this.selectee.eq(val).addClass("hide");
    }
}

//导航下面的滑线
$(".nav ul li").mouseover(function () {
    $(".nav ul li").removeClass("cur");
    $(this).addClass("cur");
});

//用来实现tab切换的一个类
function tabSwicher(option, index) {
    if (option instanceof $) {
        option = {
            fa: option.find(".tabs"),
            children: option.find(".tabs li"),
            childSel: ">li",
            showList: option.find(".tab-list > li")
        };
    }
    this.now = 0;
    if (index) {
        this.now = index;
    }
    this.fa = typeof option.fa === "string" ? $(option.fa) : option.fa;
    this.children = typeof option.children === "string" ? $(option.children) : option.children;
    this.childSel = option.childSel || "li";
    this.showList = typeof option.showList === "string" ? $(option.showList) : option.showList;
    this.init(index);
}
var tabProto = tabSwicher.prototype;
tabProto.bind = function () {
    this.fa.on("click", this.childSel, {that: this}, this.handleSwitch);
}
tabProto.handleSwitch = function (e) {
    var that = e.data.that
            , cIndex = that.children.index(this)
            ;
    if (cIndex < that.children.length && cIndex !== that.now) {
        that.hide(that.now);
        that.show(cIndex);
        that.now = cIndex;
    }
}
tabProto.show = function (index) {
    index = index == undefined ? this.now : index;
    this.showList.eq(index).css("display", "block").siblings().hide();
    this.children.eq(index).addClass("cur");
}
tabProto.hide = function (index) {
    index = index == undefined ? this.now : index;
    this.showList.eq(index).css("display", "none");
    this.children.eq(index).removeClass("cur");
}
tabProto.init = function () {
    this.bind();
    this.show();
}

var RLO = {
    login: function (userinfo) {
        $('.unlog').hide();
		if(userinfo.nickname!=''){
			$('.user-name-tag').html(userinfo.nickname.substring(0, 9));
		} else {
        	$('.user-name-tag').html(userinfo.username.substring(0, 9));
		}
        $('.loged').show();
    },
    listenLog: function () {
        var self = this;
        $(".logNreg").on("click", "a", function (e) {
            var $this = $(this)
                    , isLog = $this.hasClass("log")
                    , isReg = $this.hasClass("reg")
                    ;
            e.preventDefault();
            if (isLog) {
                QHPass.signIn(true);
            } else if (isReg) {
                QHPass.signUp(true);
            }
        });
    },
}

var sync_count = function (type) {
    var id = '';
    var is_first = true;
    if (type == 'merge') {	//整合列表
        var type_arr = new Array();
        var key = '';
        var tmp = '';
        $("span[class='read']").each(function (index, element) {
            key = $(this).attr("data-type");
            val = $(this).attr("data-value").replace("r_", "");
            id += key + ',' + val + '|';
        });

        if (!id)
            return;
        $.get('/' + type + '/count/', {id: id}, function (data) {
            if (data.success) {
                data = data.data;
                for (key in data) {
                    $("span[data-value='r_" + data[key].id + "'][data-type='" + data[key].type + "']").html("阅读(" + data[key].view + ")");
                    var text = (data[key].is_good) ? "已赞" : "点赞";
                    if (data[key].is_good) {
                        $("a[data-value='g_" + data[key].id + "']").parent().html("<span class='good'>已赞(" + data[key].good + ")</span>");
                    } else {
                        $("a[data-value='g_" + data[key].id + "']").html("点赞(" + data[key].good + ")");
                    }
                    if (data[key].is_fav) {
                        $("a[data-pk='" + data[key].id + "']").parent().html("<span class='fav'>已收(" + data[key].fav + ")</span>");
                    } else {
                        $("a[data-pk='" + data[key].id + "']").html("收藏(" + data[key].fav + ")");
                    }
                }
            }
        }, 'json');

    } else {

        $("span[class='read']").each(function (index, element) {
            if ($(this).attr("data-type") == type) {
                if (!is_first) {
                    id += ',';
                }
                id += $(this).attr("data-value").replace("r_", "");
                if (is_first) {
                    is_first = false;
                }
            }
        });
        if (!id) {
            $(".good").each(function (index, element) {
                if ($(this).attr("data-type") == type) {
                    if (!is_first) {
                        id += ',';
                    }
                    id += $(this).attr("data-value").replace("g_", "");
                    if (is_first) {
                        is_first = false;
                    }
                }
            });
        }
        if (!id)
            return;
        $.get('/' + type + '/count/', {id: id}, function (data) {
            if (data.success) {
                data = data.data[type];
                for (key in data) {
                    $("span[data-value='r_" + key + "']").html("阅读(" + data[key].view + ")");
                    var text = (data[key].is_good) ? "已赞" : "点赞";
                    if (data[key].is_good) {
                        $("a[data-value='g_" + key + "']").parent().html("<span class='good'>已赞(" + data[key].good + ")</span>");
                    } else {
                        $("a[data-value='g_" + key + "']").html("点赞(" + data[key].good + ")");
                    }
                    if (data[key].is_fav) {
                        $("a[data-pk='" + key + "']").parent().html("<span class='fav'>已收(" + data[key].fav + ")</span>");
                    } else {
                        $("a[data-pk='" + key + "']").html("收藏(" + data[key].fav + ")");
                    }
                }
            }
        }, 'json');
    }


};

var fav = function (e) {
    var $this = $(this);
    var id = $this.attr("data-pk");
    var type = $this.attr("data-type");
    QHPass.when.signIn(function () {
        $.post($this.attr("data-target"), {id: id}, function (data) {
            mynoty.ajaxShow(data);
            if (data.success && data.data) {
                $this.html("已收(" + data.data[type][id].fav + ")");
            }
        }, 'json');
    });
}

var good = function (e) {
    var $this = $(this);
//    QHPass.when.signIn(function () {
        $.post($this.attr("data-target"), {id: $this.attr("data-value").replace("g_", "")}, function (data) {
            mynoty.ajaxShow(data);
            if (data.success) {
                $this.html("已赞(" + data.data.good + ")");
            }
        }, 'json');
//    });
}

var make_comment = function (data) {
    var html = "";
    html += "<div class='comment'>";
    html += "<div class='avatar'><a href='javascript:;'><img src='" + data.image_url + "'></a></div>";
    html += "<div class='comment-main'>";
    html += "  <div class='comment-user'><a href='javascript:;'>" + data.user_name + "</a></div>";
    html += "  <p class='content'>" + data.content + "</p>";
    html += "  <div>";
    html += "    <span class='comment-time'>" + data.add_time + "</span>";
    if (data.source) {
        html += "    <div class='comment-quote'>";
        html += "      <div id='quote-content'>"
        html += "      <a href='javascript:;'>" + data.source.user_name + "</a> 说：";
        html += "      <p>" + data.source.content + "</p>";
        html += "      <span class='comment-time'>" + data.source.add_time + "</span>";
        html += "      </div>";
        html += "    </div>";
    }
    html += "    <div class='comment-action'>";
    if (data.allow_response) {
        html += "        <span class='comment-response'><a href='javascript:;' class='response' data-target='textarea-" + data.id + "'>回复</a></span>&nbsp;|&nbsp;";
    }
    html += "        <span><a href='javascript:;' class='good' data-target='" + data.good_url + "' data-value='" + data.id + "' data-type='comment'>点赞</a></span>";
    html += "    </div>";
    html += "  </div>";
    html += "  <div id='textarea-" + data.id + "' class='hide'>";
    html += "    <textarea class='response-textarea'></textarea>";
    html += "<span class='span_use_nickname' id='span_use_nickname'>";
    html += "<input type='checkbox' value='' class='use_nickname'>  <label for='use_nickname'>匿名</label>";
    html += "</span>";
    html += "    <a class='button submit' data-target-id='" + data.id + "'>发&nbsp;布</a>";
    html += "  </div>";
    html += "</div>";
    html += "</div>";
    html += "<div class='clearfix'></div>";
    return html;
}

var make_comments = function (data) {
    var html = "";
    for (k in data) {
        html += make_comment(data[k]);
    }
    return html;
}

$(function () {

    formSel.init();
    //slide.init();
    // userSel.init();
    // messageSel.init();

    QHPass.init("pcw_adlab");
    QHPass.setConfig('signIn.types', ['normal']);
    QHPass.getUserInfo(true, RLO.login, RLO.listenLog);

    $('.news-list').on('click', '.fav', fav);
    $('.news-list').on('click', '.good', good);
    $('.links-list').on('click', '.fav', fav);
    $('.links-list').on('click', '.good', good);
    $('.article-msg').on('click', '.fav', fav);
    $('.article-msg').on('click', '.good', good);
    $('.comment').on('click', '.good', good);

    $(".comment-reg").click(function () {
        QHPass.signUp(true);
    });
    $(".comment-login").click(function () {
        QHPass.when.signIn(function () {
            $(".join").hide();
            $(".reg-log textarea").first().removeAttr("disabled").show().focus();
        });
    });
    $(".comment-more").click(function () {
        var parent = $(this);
        var next_page = parseInt($(this).attr("data-page"));
        var type = parent.attr("data-type");
        var source_id = $(this).attr("data-source-id");
        $.get($(this).attr("data-target"), {"_view":"",page: $(this).attr("data-page"), type: type, source_id: source_id, page:next_page}, function (data) {
            parent.attr("data-page", next_page + 1);
            if(data){
                $(data).insertBefore($(".comment-more"));
            }else{
                $(parent).html("无更多评论");
            }
//            if (data.success) {
//                $(make_comments(data.data)).insertBefore($(".comment-more"));
//                //为所有复选框绑定事件
//                checkbox_on_click();
//                parent.attr("data-page", next_page + 1);
//            } else {
//                $(parent).html("无更多评论");
//            }
        });
    });

    var lazyTime = 150;
    var time1 = 0;
    var time2 = 0;
    var time3 = 0;
    var time4 = 0;
    var clearAllTimeOut = function () {
        clearTimeout(time1);
        clearTimeout(time2);
        clearTimeout(time3);
        clearTimeout(time4);
    }
    $('.user-center').on('mouseenter', function () {
        clearAllTimeOut();
        $('.user-links').show();
        $('.message-links').hide();
    }).on('mouseleave', function () {
        clearAllTimeOut();
        time1 = setTimeout(function () {
            $('.user-links').hide();
        }, lazyTime);
    });

    $('.user-links').on('mouseenter', function () {
        clearAllTimeOut();
    }).on('mouseleave', function () {
        clearAllTimeOut();
        time2 = setTimeout(function () {
            $('.user-links').hide();
        }, lazyTime);
    });


    $('.message-center').on('mouseenter', function () {
        clearAllTimeOut();
        $('.message-links').show();
        $('.user-links').hide();
    }).on('mouseleave', function () {
        clearAllTimeOut();
        time1 = setTimeout(function () {
            $('.message-links').hide();
        }, lazyTime);
    });

    $('.message-links').on('mouseenter', function () {
        clearAllTimeOut();
    }).on('mouseleave', function () {
        clearAllTimeOut();
        time2 = setTimeout(function () {
            $('.message-links').hide();
        }, lazyTime);
    });

    var post_comment = function (content, source_id, target_id, to, detail_title, type, callback) {
        var nick_name = $("#nick-name").val();
        if (!content || content.length < 5) {
            mynoty.error("内容不能少于五个字");
            $("#comment-content").focus();
            return false;
        }
        if (content.length >= 1000) {
            mynoty.error("内容太长");
            return false;
        }
        if (!type) {
            type = $("#source-type").val();
        }

        if (!type || !source_id) {
            mynoty.error("参数错误");
            return false;
        }
        var use_nickname = $('#use_nickname').val();
        var url = $("#post-comment-url").val();
		var stoken = $('#stoken_comment_set').val();
        var da = {nick_name: nick_name, type: type, to: to, detail_title: detail_title, content: content, source_id: source_id, target_id: target_id, use_nickname: use_nickname, stoken:stoken};
        $.post(url, da, function (data) {
            mynoty.ajaxShow(data);
            callback(data);
        }, 'json');
    }

    /* 评论 */
    $("#submit-comment").click(function () {
        var content = $("#comment-content").val();
        var source_id = $("#source-id").val();
        var to = $('.to').serialize();
        var detail_title = $('#detail_title').val();
        post_comment(content, source_id, 0, to, detail_title, 0, function (data) {
            if (data.success) {
                $("#comment-content").val('');
                $(make_comment(data.data)).insertAfter($(".comments-head"));
                $(".comment-none").hide();
            }
        });
        //评论之后锚点跳转
        window.location.hash = 'mao';
    });
    //为所有复选框绑定事件
    function checkbox_on_click() {
        $('.use_nickname').on('click', function () {
            var checked_status = $(this).prop('checked');
            $('.comment-nick-name').remove();
            if (checked_status == false) {
                $('#use_nickname').val('0');
                $('.use_nickname').removeAttr('checked');
            } else {
                $('#use_nickname').val('1');
                $(this).after("<div class=\"comment-nick-name\" style=\"display: block;\">昵称<span class=\"text-danger\">*</span><input type=\"text\" id=\"nick-name\" value=\"\" maxlength=\"8\"><span class=\"comment-nick-name\" id=\"comment-nick-name-rand\" style=\"display: inline;\"><a href=\"javascript:void(0);\" style=\"color:#4487de\">换一个</a></span></div>");
                if(!_nick_name){
                    randnicknameajax(1);
                }else{
                    $('#nick-name').val(_nick_name);
                }
                $('#comment-nick-name-rand').on('click', function () {
                    randnicknameajax(1);
                });
            }
        });
    }
    checkbox_on_click();
    /* 回复 */
    $('.comments').on('click', '.response', function () {
        var $this = $(this);
//		QHPass.when.signIn(function(){
//			$("#"+$this.attr("data-target")).toggle().focus();
//		});
        $('.response-area').remove();
        var $id = $this.attr("data-target");
        $this.parents('.comment-user').after("<div id=\"textarea-" + $id + "\" class=\"response-area\"><textarea class=\"response-textarea\"></textarea>                        <span id=\"span_use_nickname\" class=\"span_use_nickname\"><label for=\"use_nickname\">匿名</label> <input class=\"use_nickname\" type=\"checkbox\" value=\"\" /></span><a class=\"button submit\" data-bind-id=\""+$this.attr("data-bind-id")+"\" data-target-id=\"" + $id + "\">回&nbsp;复</a></div>");
        checkbox_on_click();
    });
    $('.comments').on('click', '.submit', function () {
        var id = $(this).attr("data-target-id");
        var content = $("#textarea-" + id + " textarea").val();
        var source_id = $("#source-id").val();
        if (!source_id) {
            source_id = $(this).attr("data-source-id");
        }
        var to = 'to[]=' + $(this).attr('data-bind-id');
        var detail_title = $('#detail_title').val();
        post_comment(content, source_id, id, to, detail_title, $(this).attr("data-source-type"), function (data) {
            if (data.success) {
                window.location.reload();
//				$("#textarea-"+id+" textarea").val('');
//				$(make_comment(data.data)).insertAfter($(".comments-head"));
            }
        });
        //评论之后锚点跳转
        window.location.hash = 'mao';
    });
});

$(function () {
    var is_mobile = false;
    if ($("#is-mobile").css('display') == 'none') {
        is_mobile = true;
    }
    if (is_mobile == true) {
        $(window).scroll(function () {
            if ($(window).scrollTop() > 175) {
                $(".header").css('display', 'none');
                //$(".mobile-content").css('padding-top', 50);
            }
            else {
                $(".header").css('display', 'block');
            }
        });
    }
    ;
});

window.onload = function () {
    // 获取文章图片，增加新窗口打开图片
    var imglist = $("#article_box").find("img");


    imglist.each(function () {
        if ($(this).width() > 660) {
            $(this).css({'width': '100%', 'height': 'auto'});
        }
        $(this).css('visibility', 'visible');

        var imgurl = $(this).attr("src");
        $(this).wrap('<a href="' + imgurl + '" target="_blank"></a>');
    });
}