/**
 * @class mw.boilerPlate
 * @singleton
 */

var conf = mw.config.get('wgVisualEditor');
mw.boilerPlate = {};
var wikidataResults = [];
var WIKIBASE_SYNC_URL = conf.local_server_url;
//console.log(WIKIBASE_SYNC_URL);

var datamodel = require( 'wikibase.datamodel' );

$.wikibase.statementgroupview.prototype._createStatementlistview = function () {
	var self = this,
		prefix;

	var $statementlistview = this.element.find('.wikibase-statementlistview');

	if (!$statementlistview.length) {
		$statementlistview = $('<div>').appendTo(this.element);
	}

	this.statementlistview = this.options.buildStatementListView(
		this.options.value ? this.options.value.getItemContainer() : new datamodel.StatementList(),
		$statementlistview
	);
	prefix = this.statementlistview.widgetEventPrefix;

	$statementlistview
		.on(prefix + 'toggleerror.' + this.widgetName, function (event, error) {
			self.$property.toggleClass('wb-error', Boolean(error));
		})
		.on(prefix + 'afterstopediting.' + this.widgetName, function (event, dropValue) {
			self.$property.removeClass('wb-error wb-edit');
			self._trigger('afterstopediting', null, [dropValue]);
		})
		.on(prefix + 'afterstartediting.' + this.widgetName, function (event) {
			self.$property.addClass('wb-edit');
		})
		.on(prefix + 'afterremove.' + this.widgetName, function (event) {
			self.$property.removeClass('wb-error wb-edit');
			self._trigger('afterremove');
		});

	//self.$cloneBtn.text('hello world');
	var _wikibasePropertyKey = "";
	if (self.value()) {
		_wikibasePropertyKey = self.value().getKey();
	}


	if (_wikibasePropertyKey == "P1" || _wikibasePropertyKey == "P2") {
		self.wikibasePropertyKey = _wikibasePropertyKey;
		// Only attach button for wikidata pid or qid properties which are always P1 and P2
		self.$cloneBtn.text('');
		createSynButton(self)
		// btn = $("<button>Sync</button>")

		// self.$cloneBtn.append(btn);

		// //console.log("val",self.value());
		// //var _wikibasePropertyValue = "";
		// var _wikibasePropertyValue = self.value().getItemContainer()._items[0]._claim._mainSnak._value._value;
		// self.wikibasePropertyValue = _wikibasePropertyValue;

		// console.log(self.wikibasePropertyKey,self.wikibasePropertyValue);

	} else {
		self.$cloneBtn.text('')
	}
	// console.log(JSON.stringify(self.options, null, 2));
};

$.wikibase.entityselector.prototype._initDefaultSource = function () {
	var self = this;
	wikidataResults = [];
	return function ( term ) {
		var deferred = $.Deferred(),
			hookResults = self._fireSearchHook( term );

		// clear previous error
		if ( self._error ) {
			self._error = null;
			self._cache.suggestions = null;
			self._updateMenu( [] );
		}

		$.ajax( {
			url: self.options.url,
			timeout: self.options.timeout,
			dataType: 'json',
			data: self._getSearchApiParameters( term ),
			success: function(data){
				$.ajax({
					url: WIKIBASE_SYNC_URL + '/remote-wikidata-query/' + term + "/" + self.options.type,
					crossDomain: true,
					headers: {
						"Access-Control-Allow-Origin": "*",
						"Access-Control-Request-Headers3": "x-requested-with"
					},
					success: function (data) {
						console.log(data);
						wikidataResults = data.response.search;
					}
				});
			}
		} )
			.done( function ( response, statusText, jqXHR ) {
				// T141955
				if ( response.error ) {
					deferred.reject( response.error.info );
					return;
				}

				// The default endpoint wbsearchentities responds with an array of errors.
				if ( response.errors && self.options.responseErrorFactory ) {
					var error = self.options.responseErrorFactory( response, 'search' );

					if ( error && self.options.showErrorCodes.indexOf( error.code ) !== -1 ) {
						self._error = error;
						self._cache = {};
						self._updateMenu( [] );
						deferred.reject( error.message );
						return;
					}
				}

				//TODO MERGE THE WIKIDATA RESULTS WITH RESPONSE SEARCH
				// console.log("hooksResults");
				// console.log(hookResults);
				// console.log("wikidataResults");
				// console.log(wikidataResults);
				// console.log("wikibase results");
				// console.log(response.search);
				// UPDATE THE TITLE AND SOURCE TO REFELECT WIKIDATA
				// REMOVE WIKIDATA RESULTS THAT ALREADY EXIST IN WIKIBASE USING FOREACH
				var updatedWikidataResults = removeExistingRecordsFromWikidataResults(wikidataResults, response.search)
				//console.log("updatedWikidataResults", updatedWikidataResults);
				//self._combineResults( hookResults, response.search ).then( function ( results ) {
				self._combineResults( hookResults, updatedWikidataResults ).then( function ( results ) {
					//console.log(results)
					deferred.resolve(
						results,
						term,
						response[ 'search-continue' ],
						jqXHR.getResponseHeader( 'X-Search-ID' )
					);
				} );
			} )
			.fail( function ( jqXHR, textStatus ) {
				deferred.reject( textStatus );
			} );

		return deferred.promise();
	};
};

$.wikibase.entityselector.prototype._select = function ( entityStub ) {
	//conf = mw.config.get( 'wgWikibaseSync' );
	//console.log("conf",conf)
	var id = entityStub && entityStub.id;
	this._selectedEntity = entityStub;

	if ( id ) {
		var self = this;
		if (entityStub.repository !== "local") {
			var cloningEl = '<p style="margin-top: 1.5rem;">importing...<p/>';
			$(cloningEl).insertAfter(self.focused);
			//remote source, clone

			//api call
			var full_endpoint = WIKIBASE_SYNC_URL + '/import-wikidata-item/' + id;
			$.ajax({
				url: full_endpoint,
				crossDomain: true,
				headers: {
					// "accept": "application/json",
					"Access-Control-Allow-Origin": "*",
					"Access-Control-Request-Headers3": "x-requested-with"
				},
				success: function (data) {
					console.log(data);
					if (data.pid) {
						$(self.focused).siblings('p').remove();
						id = data.pid;
						//console.log(self._selectedEntity);

						if (self.options.type.toLowerCase() == "property") {
							self._selectedEntity.id = id;
							self._selectedEntity.title = "Property:" + id;
							self._selectedEntity.repository = "local";
							self._selectedEntity.url = "http://localhost/wiki/Property:" + id;
							self._selectedEntity.pageid = null;
						} else if (self.options.type.toLowerCase() == "item"){
							self._selectedEntity.id = id;
							self._selectedEntity.title = id;
							self._selectedEntity.repository = "local";
							self._selectedEntity.url = "http://localhost/wiki/" + id;
							self._selectedEntity.pageid = null;
						}

						//this._selectedEntity = { id: id };
						//TODO
						self._trigger( 'selected', null, [ id ] );
					}
				}
			});
		} else {
			this._trigger( 'selected', null, [ id ] );
		}
	}
};

function createSynButton(_context) {
	btn = $("<button>sync</button>")
	btn.css("margin-top", ".5rem");
	btn.css("color", "#0645ad");
	btn.css("background-color", "white");
	btn.css("border-color", "#0645ad");
	btn.css("border-radius", "5px");

	_context.$cloneBtn.append(btn);

	var _wikibasePropertyValue = _context.value().getItemContainer()._items[0]._claim._mainSnak._value._value;
	self.wikibasePropertyValue = _wikibasePropertyValue;

	//console.log(_context.wikibasePropertyKey,_context.wikibasePropertyValue);

	btn.on('click', function () {
		btn.text("syncing...");
		//api call
		var full_endpoint = WIKIBASE_SYNC_URL + '/sync/' + self.wikibasePropertyValue;
		$.ajax({
			url: full_endpoint,
			crossDomain: true,
			headers: {
				// "accept": "application/json",
				"Access-Control-Allow-Origin": "*",
				"Access-Control-Request-Headers3": "x-requested-with"
			},
			success: function (data) {
				if (data.completed) {
					console.log(data);
					location.reload();
				}


			}
		});
	});
};


function removeExistingRecordsFromWikidataResults(wikidataResults, localResults){
	if (!wikidataResults || !localResults){
		return wikidataResults;
	}
	var updatedResults = [];
	localResults.concat(wikidataResults).forEach(function (element) {
		var index = updatedResults.findIndex(function(x){
			return x.label.toLowerCase().trim() == element.label.toLowerCase().trim() && x.description.toLowerCase().trim() == element.description.toLowerCase().trim()
		})
		if (index == -1) {
			if (element.repository.toLowerCase() !== "local") {
				element.label = "[source: wikidata] " + element.label
			}
			updatedResults.push(element);
		}
	})
	return updatedResults


};
