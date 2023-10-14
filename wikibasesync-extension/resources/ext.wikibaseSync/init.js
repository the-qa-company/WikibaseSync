/**
 * @class mw.boilerPlate
 * @singleton
 */

var conf = mw.config.get('wgVisualEditor');
mw.boilerPlate = {};
var wikidataResults = [];
var WIKIBASE_SYNC_URL = conf.wikibasesync_server_url;
var API_KEY = conf.api_key;
var SERVER = conf.Server;

var datamodel = require('wikibase.datamodel');

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


    var _wikibasePropertyKey = "";
    console.log('self.value()', self.value())
    if (self.value()) {
        _wikibasePropertyKey = self.value().getKey();

        //PREFERRED APPROACH
        // if ($("a:contains('Wikidata QID')")) {
        // 	if (count == 0){
        // 		createSyncButtons(self);
        // 		count = count + 1;
        // 	}
        // };
    }

    //ALTERNATIVE APPROACH
    if (_wikibasePropertyKey == conf.PID || _wikibasePropertyKey == conf.QID) {
        self.wikibasePropertyKey = _wikibasePropertyKey;
        createSyncButton(self);
        createSyncLabelButton(self);
    }
};

$.wikibase.entityselector.prototype._initDefaultSource = function () {
    var self = this;
    wikidataResults = [];
    return function (term) {
        var deferred = $.Deferred(),
            hookResults = self._fireSearchHook(term);

        // clear previous error
        if (self._error) {
            self._error = null;
            self._cache.suggestions = null;
            self._updateMenu([]);
        }

        $.ajax({
            url: self.options.url,
            timeout: self.options.timeout,
            dataType: 'json',
            data: self._getSearchApiParameters(term),
            success: function (data) {
                $.ajax({
                    url: WIKIBASE_SYNC_URL + '/remote-wikidata-query?query_string=' + term + "&query_type=" + self.options.type + "&api_key=" + API_KEY,
                    crossDomain: true,
                    headers: {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Request-Headers3": "x-requested-with"
                    },
                    success: function (data2) {
                        wikidataResults = data2.response.search;
                    }
                })
                    .done(function (response, statusText, jqXHR) {
                        // T141955
                        if (response.error) {
                            deferred.reject(response.error.info);
                            return;
                        }

                        // The default endpoint wbsearchentities responds with an array of errors.
                        if (response.errors && self.options.responseErrorFactory) {
                            var error = self.options.responseErrorFactory(response, 'search');

                            if (error && self.options.showErrorCodes.indexOf(error.code) !== -1) {
                                self._error = error;
                                self._cache = {};
                                self._updateMenu([]);
                                deferred.reject(error.message);
                                return;
                            }
                        }


                        // UPDATE THE TITLE AND SOURCE TO REFLECT WIKIDATA
                        // REMOVE WIKIDATA RESULTS THAT ALREADY EXIST IN WIKIBASE USING FOREACH
                        var updatedWikidataResults = removeExistingRecordsFromWikidataResults(wikidataResults, data.search)
                        self._combineResults(hookResults, updatedWikidataResults).then(function (results) {
                            deferred.resolve(
                                results,
                                term,
                                response['search-continue'],
                                jqXHR.getResponseHeader('X-Search-ID')
                            );
                        });
                    })
                    .fail(function (jqXHR, textStatus) {
                        deferred.reject(textStatus);
                    });
            }
        })

        return deferred.promise();
    };
};

$.wikibase.entityselector.prototype._select = function (entityStub) {
    var id = entityStub && entityStub.id;
    this._selectedEntity = entityStub;

    if (id) {
        var self = this;
        if (entityStub.repository !== "local") {
            var cloningEl = '<p style="margin-top: 1.5rem;">importing...<p/>';
            $(cloningEl).insertAfter(self.focused);
            //remote source, clone

            //api call
            var full_endpoint = WIKIBASE_SYNC_URL + '/import-wikidata-item?q_id=' + id + "&api_key=" + API_KEY;
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

                        if (self.options.type.toLowerCase() == "property") {
                            self._selectedEntity.id = id;
                            self._selectedEntity.title = "Property:" + id;
                            self._selectedEntity.repository = "local";
                            self._selectedEntity.url = SERVER + "/wiki/Property:" + id;
                            self._selectedEntity.pageid = null;
                        } else if (self.options.type.toLowerCase() == "item") {
                            self._selectedEntity.id = id;
                            self._selectedEntity.title = id;
                            self._selectedEntity.repository = "local";
                            self._selectedEntity.url = SERVER + "/wiki/" + id;
                            self._selectedEntity.pageid = null;
                        }

                        self._trigger('selected', null, [id]);
                    }
                }
            });
        } else {
            this._trigger('selected', null, [id]);
        }
    }
};


// overwrite search result default behaviour sec
$.wikibase.entitysearch.prototype._initMenu = function (ooMenu) {
    var PARENT = $.wikibase.entityselector;
    PARENT.prototype._initMenu.apply(this, arguments);

    if (this.options.suggestionsPlaceholder) {
        ooMenu.option('customItems').unshift(this.options.suggestionsPlaceholder);
    }

    ooMenu.element.addClass('wikibase-entitysearch-list');

    $(ooMenu)
        .off('selected')
        .on('selected.entitysearch', function (event, item) {
            if (event.originalEvent
                // && /^key/.test( event.originalEvent.type )
                && !(item instanceof $.ui.ooMenu.CustomItem)
            ) {
                var itemEntityStub = item.getEntityStub();
                if (itemEntityStub) {
                    if (itemEntityStub.repository.toLowerCase() === "wikidata") {

                        $("a[tabindex='-1']").click(function (e) {
                            e.preventDefault();
                        });

                        //api call
                        var full_endpoint = WIKIBASE_SYNC_URL + '/import-wikidata-item?q_id=' + itemEntityStub.id + "&api_key=" + API_KEY;
                        $.ajax({
                            url: full_endpoint,
                            crossDomain: true,
                            //async: false,
                            //global: false,
                            headers: {
                                "Access-Control-Allow-Origin": "*",
                                "Access-Control-Request-Headers3": "x-requested-with"
                            },
                            success: function (data) {
                                console.log("response: ", data);
                                //window.history.back();
                                window.location.replace(SERVER + '/wiki/item:' + data.pid);

                            }
                        });
                    } else {
                        window.location.href = item.getEntityStub().url;
                    }
                }
            }
        });

    return ooMenu;
}

function createSyncButtons(_context) {
    btn = $("<button>sync</button>")
    btn2 = $("<button>sync label</button>")
    //btn.css("margin-top", ".5rem");
    btn.css("display", "block");
    //btn.css("margin-left", "5px");
    btn.css("color", "#0645ad");
    btn.css("background-color", "white");
    btn.css("border-color", "#0645ad");
    btn.css("border-radius", "5px");

    //btn2.css("margin-left", "5px");
    btn2.css("margin-top", ".3rem");
    btn2.css("display", "block");
    btn2.css("color", "#0645ad");
    btn2.css("background-color", "white");
    btn2.css("border-color", "#0645ad");
    btn2.css("border-radius", "5px");

    _context.$propertyLabel.append(btn);
    _context.$propertyLabel.append(btn2);

    var _wikibasePropertyValue = _context.value().getItemContainer()._items[0]._claim._mainSnak._value._value;
    self.wikibasePropertyValue = _wikibasePropertyValue;

    //console.log(_context.wikibasePropertyKey,_context.wikibasePropertyValue);

    btn.on('click', function () {
        btn.text("syncing...");
        //api call
        full_endpoint = WIKIBASE_SYNC_URL + '/sync?q_id=' + self.wikibasePropertyValue + "&api_key=" + API_KEY;
        $.ajax({
            url: full_endpoint,
            crossDomain: true,
            headers: {
                // "accept": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Request-Headers3": "x-requested-with"
            },
            success: function (data) {
                if (data) {
                    location.reload();
                }


            }
        });
    });

    btn2.on('click', function () {
        btn2.text("syncing...");
        //api call
        var full_endpoint = WIKIBASE_SYNC_URL + '/import-wikidata-item?q_id=' + self.wikibasePropertyValue + "&api_key=" + API_KEY;
        $.ajax({
            url: full_endpoint,
            crossDomain: true,
            headers: {
                // "accept": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Request-Headers3": "x-requested-with"
            },
            success: function (data) {
                if (data) {
                    //console.log(data);
                    location.reload();
                }


            }
        });
    });
};

function createSyncButton(_context) {
    btn = $("<button id='wbsync'>sync</button>")
    btn.css("display", "block");
    btn.css("color", "#0645ad");
    btn.css("background-color", "white");
    btn.css("border-color", "#0645ad");
    btn.css("border-radius", "5px");

    _context.$propertyLabel.append(btn);

    var _wikibasePropertyValue = _context.value().getItemContainer()._items[0]._claim._mainSnak._value._value;
    self.wikibasePropertyValue = _wikibasePropertyValue;

    btn.on('click', function () {
        btn.text("syncing...");
        btn.prop("disabled", true);
        //disable other sync button
        $('#wbsynclabel').prop("disabled", true);
        //api call
        full_endpoint = WIKIBASE_SYNC_URL + '/sync?q_id=' + self.wikibasePropertyValue + "&api_key=" + API_KEY;
        $.ajax({
            url: full_endpoint,
            crossDomain: true,
            headers: {
                // "accept": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Request-Headers3": "x-requested-with"
            },
            success: function (data) {
                if (data) {
                    console.log(data);
                    location.reload();
                }


            }
        });
    });
};

function createSyncLabelButton(_context) {
    btn2 = $("<button id='wbsynclabel'>sync label</button>")
    //btn2.css("margin-left", "5px");
    btn2.css("margin-top", ".3rem");
    btn2.css("display", "block");
    btn2.css("color", "#0645ad");
    btn2.css("background-color", "white");
    btn2.css("border-color", "#0645ad");
    btn2.css("border-radius", "5px");

    _context.$propertyLabel.append(btn2);

    var _wikibasePropertyValue = _context.value().getItemContainer()._items[0]._claim._mainSnak._value._value;
    self.wikibasePropertyValue = _wikibasePropertyValue;

    //console.log(_context.wikibasePropertyKey,_context.wikibasePropertyValue);

    btn2.on('click', function () {
        btn2.text("syncing...");
        btn2.prop("disabled", true);
        //disable other sync button
        $('#wbsync').prop("disabled", true);
        //api call
        var full_endpoint = WIKIBASE_SYNC_URL + '/import-wikidata-item?q_id=' + self.wikibasePropertyValue + "&api_key=" + API_KEY;
        $.ajax({
            url: full_endpoint,
            crossDomain: true,
            headers: {
                // "accept": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Request-Headers3": "x-requested-with"
            },
            success: function (data) {
                if (data) {
                    console.log(data);
                    location.reload();
                }


            }
        });
    });
};


function removeExistingRecordsFromWikidataResults(wikidataResults, localResults) {
    if (!wikidataResults || !localResults) {
        return wikidataResults;
    }
    var updatedResults = [];
    localResults.concat(wikidataResults).forEach(function (element) {
        var index = updatedResults.findIndex(function (x) {
            return x.label.toLowerCase().trim() == element.label.toLowerCase().trim() && x.description.toLowerCase().trim() == element.description.toLowerCase().trim()
        })
        if (index == -1) {
            if (element.repository.toLowerCase() !== "local") {
                element.label = "[clone from wikidata:] " + element.label
            }
            updatedResults.push(element);
        }
    })
    return updatedResults
    
};

