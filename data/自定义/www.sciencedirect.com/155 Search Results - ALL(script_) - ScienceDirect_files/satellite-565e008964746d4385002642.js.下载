_satellite.pageBottom = function() {
	if (window.pageData && pageData.isLoaded) {
		_satellite.initialized && (_satellite.pageBottomFired = !0, _satellite.firePageLoadEvent("pagebottom"))
	}
}

var pageDataTracker = {
	eventCookieName: 'eventTrack'
	
	,trackPageLoad: function(data) {
		if (window.pageData && ((pageData.page && pageData.page.noTracking == 'true') || pageData.isLoaded)) {
			return false;
		}
		
		if (data) {
			window.pageData = data;
		}
		
		this.setAnalyticsData();
		
		// handle any cookied event data
		this.getEvents();
		
		pageData.isLoaded = true;
		_satellite.pageBottom();
	}
	,trackEvent: function(event, data) {
		if (window.pageData && pageData.page && pageData.page.noTracking == 'true') {
			return false;
		}
		
		if (event) {
			window.eventData = data ? data : {};
			window.eventData.eventName = event;
			this.handleEventData(event, data);
			
			_satellite.track(event);
		}
	}
	
	,setAnalyticsData: function() {
		pageData.page.analyticsPagename = pageData.page.productName + ':' + pageData.page.name;
		
		var pageEls = pageData.page.name.indexOf(':') > -1 ? pageData.page.name.split(':') : ['other'];
		pageData.page.sectionName = pageData.page.productName + ':' + pageEls[0];
	}
	
	,getEvents: function() {
		pageData.savedEvents = {};
		pageData.eventList = [];
		
		var val = this.getCookie(this.eventCookieName);
		if (val) {
			pageData.savedEvents = val;
		}
		
		this.deleteCookie(this.eventCookieName);
	}
	
	,handleEventData: function(event, data) {
		var val;
		switch(event) {
			case 'newPage':
				if (data) {
					// overwrite page-load object
					if (data.page && typeof(data.page) == 'object') {
						for (var x in pageData.page) {
							if (data.page[x]) {
								pageData.page[x] = data.page[x];
							}
						}
					}
					if (data.visitor && typeof(data.visitor) == 'object') {
						for (var x in pageData.visitor) {
							if (data.visitor[x]) {
								pageData.visitor[x] = data.visitor[x];
							}
						}
					}
				}
				this.setAnalyticsData();
			case 'searchResultsUpdated':
				if (data) {
					// overwrite page-load object
					if (data.search && typeof(data.search) == 'object') {
						window.eventData.search.resultsPosition = '';
						pageData.search = pageData.search || {};
						var fields = ['advancedCriteria', 'criteria', 'currentPage', 'dataFormCriteria', 'facets', 'resultsByType', 'resultsPerPage', 'sortType', 'totalResults', 'type'];
						for (var i=0; i<fields.length; i++) {
							if (data.search[fields[i]]) {
								pageData.search[fields[i]] = data.search[fields[i]];
							}
						}
					}
				}
				this.setAnalyticsData();
				break;
			case 'navigationClick':
				if (data && data.link) {
					window.eventData.navigationLink = {
						name: ((data.link.location || 'no location') + ':' + (data.link.name || 'no name'))
					};
				}
				break;
			case 'autoSuggestClick':
				if (data && data.search) {
					val = {
						autoSuggestSearchData: ('letterct:' + (data.search.suggestedLetterCount || 'none') + '|resultct:' + (data.search.suggestedResultCount || 'none') + '|clickpos:' + (data.search.suggestedClickPosition || 'none')).toLowerCase()
						,autoSuggestSearchTerm: (data.search.typedTerm || '')
					};
				}
				break;
			case 'linkOut':
				if (data && data.content && data.content.length > 0) {
					window.eventData.linkOut = data.content[0].linkOut;
					window.eventData.referringProduct = _satellite.getDataElement('Page - Product Name') + ':' + data.content[0].id;
				}
				break;
			case 'contentInteraction':
				if (data && data.action) {
					window.eventData.action.name = pageData.page.productName + ':' + data.action.name;
				}
				break;
			case 'searchWithinContent':
				if (data && data.search) {
					window.pageData.search = window.pageData.search || {};
					pageData.search.withinContentCriteria = data.search.withinContentCriteria;
				}
				break;
			case 'contentShare':
				if (data && data.content) {
					window.eventData.sharePlatform = data.content[0].sharePlatform;
				}
				break;
			case 'contentLinkClick':
				if (data && data.link) {
					window.eventData.action = { name: pageData.page.productName + ':' + (data.link.type || 'no link type') + ':' + (data.link.name || 'no link name') };
				}
				break;
			case 'contentWindowLoad':
			case 'contentTabClick':
				if (data && data.content) {
					window.eventData.tabName = data.content[0].tabName || '';
					window.eventData.windowName = data.content[0].windowName || '';
				}
				break;
			case 'userProfileUpdate':
				if (data && data.user) {
					if (Object.prototype.toString.call(data.user) === "[object Array]") {
						window.eventData.user = data.user[0];
					}
				}
				break;
		}
		
		if (val) {
			this.setCookie(this.eventCookieName, val);
		}
	}
	
	,getConsortiumAccountId: function() {
		var id = '';
		if (window.pageData && pageData.visitor && (pageData.visitor.consortiumId || pageData.visitor.accountId)) {
			id = (pageData.visitor.consortiumId || 'no consortium ID') + '|' + (pageData.visitor.accountId || 'no account ID'); 
		}
		
		return id;
	}
	
	,getSearchClickPosition: function() {
		if (window.eventData && eventData.search && eventData.search.resultsPosition) {
			var pos = parseInt(eventData.search.resultsPosition), clickPos;
			if (!isNaN(pos)) {
				var page = pageData.search.currentPage ? parseInt(pageData.search.currentPage) : '', perPage = pageData.search.resultsPerPage ? parseInt(pageData.search.resultsPerPage) : '';
				if (!isNaN(page) && !isNaN(perPage)) {
					clickPos = pos + ((page - 1) * perPage);
								6 + ((3-1) * 25)
				}
			}
			return clickPos ? clickPos.toString() : eventData.search.resultsPosition;
		}
		return '';
	}
	
	,getSearchFacets: function() {
		var facetList = '';
		if (window.pageData && pageData.search && pageData.search.facets) {
			for (var i=0; i<pageData.search.facets.length; i++) {
				var f = pageData.search.facets[i];
				facetList += (facetList ? '|' : '') + f.name + '=' + f.values.join('^');
			}
		}
		return facetList;
	}
	
	,getSearchResultsByType: function() {
		var resultTypes = '';
		if (window.pageData && pageData.search && pageData.search.resultsByType) {
			for (var i=0; i<pageData.search.resultsByType.length; i++) {
				var r = pageData.search.resultsByType[i];
				resultTypes += (resultTypes ? '|' : '') + r.name + (r.results || r.values ? '=' + (r.results || r.values) : '');
			}
		}
		return resultTypes;
	}
	
	,getJournalInfo: function() {
		var info = '';
		if (window.pageData && pageData.journal) {
			var journal = pageData.journal;
			return (journal.name || 'no name') + '|' + (journal.specialty || 'no specialty') + '|' + (journal.section || 'no section') + '|' + (journal.issn || 'no issn') + '|' + (journal.issueNumber || 'no issue #') + '|' + (journal.volumeNumber || 'no volume #');
		}
		return info;
	}
	
	,getBibliographicInfo: function(doc) {
		if (!doc || !(doc.indexTerms || doc.publicationType || doc.publicationRights || doc.volumeNumber || doc.issueNumber || doc.subjectAreas || doc.isbn)) {
			return '';
		}
		
		var terms = doc.indexTerms ? doc.indexTerms.split('+') : '';
		if (terms) {
			terms = terms.slice(0, 5).join('+');
			terms = terms.length > 100 ? terms.substring(0, 100) : terms;
		}
		
		var areas = doc.subjectAreas ? doc.subjectAreas.split('>') : '';
		if (areas) {
			areas = areas.slice(0, 5).join('>');
			areas = areas.length > 100 ? areas.substring(0, 100) : areas;
		}
		
		var biblio	= (doc.publisher || 'none')
					+ '^' + (doc.publicationType || 'none')
					+ '^' + (doc.publicationRights || 'none')
					+ '^' + (terms || 'none')
					+ '^' + (doc.volumeNumber || 'none')
					+ '^' + (doc.issueNumber || 'none')
					+ '^' + (areas || 'none')
					+ '^' + (doc.isbn || 'none');
		
		return this.stripProductDelimiters(biblio).toLowerCase();
	}
	
	,getContentItem: function() {
		var docs = window.eventData && eventData.content ? eventData.content : pageData.content;
		if (docs && docs.length > 0) {
			return docs[0];
		}
	}
	
	,getFormattedDate: function(ts) {
		if (!ts) {
			return '';
		}
		
		var d = new Date(parseInt(ts));
		
		// now do formatting
		var year = d.getFullYear()
			,month = ((d.getMonth() + 1) < 10 ? '0' : '') + (d.getMonth() + 1)
			,date = (d.getDate() < 10 ? '0' : '') + d.getDate()
			,hours = d.getHours() > 12 ? d.getHours() - 12 : d.getHours()
			,mins = (d.getMinutes() < 10 ? '0' : '') + d.getMinutes()
			,ampm = d.getHours() > 12 ? 'pm' : 'am';
		
		hours = (hours < 10 ? '0' : '') + hours;
		return year + '-' + month + '-' + date;
	}
	
	,setProductsVariable: function() {
		var prodList = window.eventData && eventData.content ? eventData.content : pageData.content
			,prods = [];
		if (prodList) {
			for (var i=0; i<prodList.length; i++) {
				if (prodList[i].id || prodList[i].type || prodList[i].publishDate || prodList[i].onlineDate) {
					if (!prodList[i].id) {
						prodList[i].id = 'no id';
					}
					var prodName = (pageData.page.productName || 'xx').toLowerCase();
					if (prodList[i].id.indexOf(prodName + ':') != 0) {
						prodList[i].id = prodName + ':' + prodList[i].id;
					}
					prodList[i].id = this.stripProductDelimiters(prodList[i].id);
					var merch = [];
					if (prodList[i].format) {
						merch.push('evar17=' + this.stripProductDelimiters(prodList[i].format.toLowerCase()));
					}
					if (prodList[i].type) {
						merch.push('evar20=' + this.stripProductDelimiters(prodList[i].type.toLowerCase()));
					}
					if (prodList[i].title) {
						merch.push('evar75=' + this.stripProductDelimiters(prodList[i].title.toLowerCase()));
					}
					if (prodList[i].breadcrumb) {
						merch.push('evar63=' + this.stripProductDelimiters(prodList[i].breadcrumb).toLowerCase());
					}
					if (prodList[i].onlineDate && prodList[i].publishDate) {
						merch.push('evar38=' + this.stripProductDelimiters(pageDataTracker.getFormattedDate(prodList[i].onlineDate) + '^' + pageDataTracker.getFormattedDate(prodList[i].publishDate)));
					}
					if (prodList[i].mapId) {
						merch.push('evar70=' + this.stripProductDelimiters(prodList[i].mapId));
					}
					if (prodList[i].status) {
						merch.push('evar73=' + this.stripProductDelimiters(prodList[i].status));
					}
					
					var biblio = this.getBibliographicInfo(prodList[i]);
					if (biblio) {
						merch.push('evar28=' + biblio);
					}
					
					if (prodList[i].turnawayId) {
						pageData.eventList.push('product turnaway');
					}
					
					prods.push([
						''					// empty category
						,prodList[i].id		// id
						,''					// qty
						,''					// price
						,''					// events
						,merch.join('|')	// merchandising eVars
					].join(';'));
				}
			}
		}
		
		return prods.join(',');
	}
	
	,stripProductDelimiters: function(val) {
		if (val) {
			return val.replace(/\;|\||\,/gi, '-');
		}
	}
	
	,setCookie: function(name, value, seconds, domain) {
		domain = document.location.hostname;
		var expires = '';
		var expiresNow = '';
		var date = new Date();
		date.setTime(date.getTime() + (-1 * 1000));
		expiresNow = "; expires=" + date.toGMTString();

		if (typeof(seconds) != 'undefined') {
			date.setTime(date.getTime() + (seconds * 1000));
			expires = '; expires=' + date.toGMTString();
		}
		
		var type = typeof(value);
		type = type.toLowerCase();
		if (type != 'undefined' && type != 'string') {
			value = JSON.stringify(value);
		}

		// fix scoping issues
		// keep writing the old cookie, but make it expire
		document.cookie = name + '=' + value + expiresNow + '; path=/';
		
		// now just set the right one
		document.cookie = name + '=' + value + expires + '; path=/; domain=' + domain;
	}

	,getCookie: function(name) {
		name = name + '=';
		var carray = document.cookie.split(';'), value;

		for (var i=0; i<carray.length; i++) {
			var c = carray[i];
			while (c.charAt(0) == ' ') {
				c = c.substring(1, c.length);
			}
			if (c.indexOf(name) == 0) {
				value = c.substring(name.length, c.length);
				try {
					value = JSON.parse(value);
				} catch(ex) {}
				
				return value;
			}
		}

		return null;
	}
	
	,deleteCookie: function(name) {
		this.setCookie(name, '', -1);
		this.setCookie(name, '', -1, document.location.hostname);
	}
	
	,mapAdobeVars: function(s) {
		var vars = {
			pageName	: 'Page - Analytics Pagename'
			,channel	: 'Page - Section Name'
			,campaign	: 'Campaign - ID'
			,prop1		: 'Visitor - Account ID'
			,prop2		: 'Page - Product Name'
			,prop4		: 'Page - Type'
			,prop6		: 'Search - Type'
			,prop7		: 'Search - Facet List'
			,prop8		: 'Search - Feature Used'
			,prop12		: 'Visitor - User ID'
			,prop13		: 'Search - Sort Type'
			,prop14		: 'Page - Load Time'
			,prop16		: 'Page - Business Unit'
			,prop21		: 'Search - Criteria'
			,prop24		: 'Page - Language'
			,prop25		: 'Page - Product Feature'
			,prop30		: 'Visitor - IP Address'
			,prop60		: 'Search - Data Form Criteria'
			,eVar3		: 'Search - Total Results'
			,eVar7		: 'Visitor - Account Name'
			,eVar15		: 'Event - Search Results Click Position'
			,eVar19		: 'Search - Advanced Criteria'
			,eVar21		: 'Promo - Clicked ID'
			,eVar22		: 'Page - Test ID'
			,eVar27		: 'Event - AutoSuggest Search Data'
			,eVar33		: 'Visitor - Access Type'
			,eVar41		: 'Visitor - Industry'
			,eVar42		: 'Visitor - SIS ID'
			,eVar43		: 'Page - Error Type'
			,eVar48		: 'Email - Recipient ID'
			,eVar51		: 'Email - Message ID'
			,eVar60		: 'Search - Within Content Criteria'
			,eVar61		: 'Search - Within Results Criteria'
			,eVar62		: 'Search - Result Types'
			,eVar74		: 'Page - Journal Info'
			,eVar76		: 'Email - Broadlog ID'
			,list3		: 'Promo - IDs'
		};
		
		for (var i in vars) {
			s[i] = s[i] ? s[i] : _satellite.getDataElement(vars[i]);
		}
	}
};
