$(document).ready(function(){
	$(".menu-toggle-wrapper").css("height",window.innerHeight+'px');

	var sidebar_state = localStorage.getItem("sidebar_state");
	if (sidebar_state === "in") {
		$("#wrapper").toggleClass("toggled");
		$(".read_nav_out").show();
		$(".read_nav_in").hide();
	} else {
		$(".read_nav_in").show();
		$(".read_nav_out").hide();
	}

});

$(document).ready(function(){
	$("#id_language").on("change keyup", function () {
		$(this).closest("form").submit();
	});
});

/* Collections */

glyph_opts = {
    map: {
      doc: "glyphicon glyphicon-file",
      docOpen: "glyphicon glyphicon-file",
      checkbox: "glyphicon glyphicon-unchecked",
      checkboxSelected: "glyphicon glyphicon-check",
      checkboxUnknown: "glyphicon glyphicon-share",
      dragHelper: "glyphicon glyphicon-play",
      dropMarker: "glyphicon glyphicon-arrow-right",
      error: "glyphicon glyphicon-warning-sign",
      expanderClosed: "glyphicon glyphicon-plus-sign",
      expanderLazy: "glyphicon glyphicon-plus-sign",  // glyphicon-expand
      expanderOpen: "glyphicon glyphicon-minus-sign",  // glyphicon-collapse-down
      folder: "glyphicon glyphicon-folder-close",
      folderOpen: "glyphicon glyphicon-folder-open",
      loading: "glyphicon glyphicon-refresh"
    }
  };
/* The fancytree rendering */
$(document).ready(function(){

    	$(".menu-toggle").click(function(e) {

	   if($(this).attr("id") === "menu-toggle-in"){
		$(".read_nav_out").show();
		$(".read_nav_in").hide();
		localStorage.setItem("sidebar_state", "in");
	   }else{
		$(".read_nav_out").hide();
		$(".read_nav_in").show();
		localStorage.setItem("sidebar_state", "out");
	   }
           $("#wrapper").toggleClass("toggled");
           e.preventDefault();

    	});
	if(typeof t_data === "undefined") t_data = [];
//	$(".pager").hide();
	$("#collections_tree").fancytree({
		  source: t_data,  //source in from transkribus
		  extensions: ["glyph", "wide"],
		  glyph: glyph_opts,
		  checkbox: true,
		  selectMode: 2,
		  loadChildren: function(event, data) {
			console.log("Loaded children...",data);
		  },
		  activate: function(event, data){
			var node = data.node,
			orgEvent = data.originalEvent;
			console.log("active node: ",data);
			$(".pager").show();
			$(".documents_intro").hide();
			if(node.isFolder()){ //we have a document
				//put the page thumbs back to small
				$(".page_thumb").show().removeClass("col-md-12").addClass("col-md-3");
				//hide other documents	
				$("#doc_"+node.data.docId).siblings(".document_thumbs").hide();
				//show active document
				$("#doc_"+node.data.docId).show().find("span.page_title").html("");

			}else{ //we have a page
				//first show the doc div that this page is in
				$("#page_"+node.key).parents(".document_thumbs").siblings().hide();
				$("#page_"+node.key).parents(".document_thumbs").show();

				//hide all the other pages
				$("#page_"+node.key).siblings(".page_thumb").hide();
				//show active page and make it full size (of panel)
				$("#page_"+node.key).show().removeClass("col-md-3", function(){
					$(this).addClass("col-md-12");
				});

				//update the page_title span in the document h4
				var page_link = "/library/page/"+node.data.collId+"/"+node.data.docId+"/"+node.data.pageNr;

				$("#page_"+node.key).parents(".document_thumbs").find("span.page_title > a").html(node.title).attr("href",page_link);
			}
		   },
	}); //endof fancytree

	/*panel expand/shrink (possibly not used*/
	$(".panel-expand").click(function(){
		var button = this;
//		$(this).parents(".expandable").removeClass("col-md-4", function(){
	
		var class_to_remove = ($(this).parents(".expandable").attr("class").match(/(^|\s)col-md-\S+/g) || []).join(' ');
		$(this).parents(".expandable").removeClass(class_to_remove, function(){

			$(this).addClass("col-md-12");
			$(button).hide(function(){
				$(button).siblings(".panel-shrink").attr("data-return-class",class_to_remove);
				$(button).siblings(".panel-shrink").show()
			});

		});
	});
	$(".panel-shrink").click(function(){
		var button = this;
		var class_to_reinstate = $(button).attr("data-return-class");
		$(this).parents(".expandable").addClass(class_to_reinstate, function(){
			$(this).removeClass("col-md-12");
			$(button).hide(function(){$(button).siblings(".panel-expand").show()});
		});
	});

});


    Status API Training Shop Blog About 

    © 2016 GitHub, Inc. Terms Privacy Security Contact Help 


