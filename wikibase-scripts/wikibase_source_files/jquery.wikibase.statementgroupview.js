function createSynButton(_context) {
	btn = $("<button>sync</button>")
	btn.css("margin-top",".5rem");
	btn.css("color","#0645ad");
	btn.css("background-color","white");
	btn.css("border-color","#0645ad");
	btn.css("border-radius","5px");

	_context.$cloneBtn.append(btn);

	var _wikibasePropertyValue = _context.value().getItemContainer()._items[0]._claim._mainSnak._value._value;
	self.wikibasePropertyValue = _wikibasePropertyValue;

	//console.log(_context.wikibasePropertyKey,_context.wikibasePropertyValue);

	btn.on('click', function () {
		btn.text("syncing...")
		//api call
		var WIKIBASE_SYNC_URL = "http://127.0.0.1:5000/";
		var full_endpoint = WIKIBASE_SYNC_URL + 'sync/' + self.wikibasePropertyValue;
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
					location.reload();
				}


			}
		});
	});
}

( function () {
	'use strict';

	var PARENT = $.ui.TemplatedWidget,
		datamodel = require( 'wikibase.datamodel' );

	/**
	 * View for displaying `datamodel.Statement` objects grouped by their main `Snak`'s
	 * `Property` id by managing a list of `jQuery.wikibase.statementview` widgets encapsulated by a
	 * `jquery.wikibase.statementlistview` widget.
	 *
	 * @see datamodel.StatementGroup
	 * @extends jQuery.ui.TemplatedWidget
	 * @license GPL-2.0-or-later
	 * @author H. Snater < mediawiki@snater.com >
	 *
	 * @constructor
	 *
	 * @param {Object} options
	 * @param {datamodel.StatementGroup} [options.value=null]
	 *        The `Statements` to be displayed by this view. If `null`, the view will only display an
	 *        "add" button to add new `Statements`.
	 * @param {wikibase.entityIdFormatter.EntityIdHtmlFormatter} options.entityIdHtmlFormatter
	 *        Required for dynamically rendering links to `Entity`s.
	 * @param {Function} options.buildStatementListView
	 */
	/**
	 * @event afterremove
	 * Triggered after a `statementview` was removed from the `statementlistview` encapsulated by this
	 * `statementgroupview`.
	 * @param {jQuery.Event} event
	 */
	$.widget( 'wikibase.statementgroupview', PARENT, {
		/**
		 * @inheritdoc
		 * @protected
		 */
		wikibasePropertyKey: "",
		wikibasePropertyValue: "",
		options: {
			template: 'wikibase-statementgroupview',
			templateParams: [
				'', // label
				'', // statementlistview widget
				'', // html id attribute
				'', // property id
				'', // clone btn
			],
			templateShortCuts: {
				$property: '.wikibase-statementgroupview-property',
				$propertyLabel: '.wikibase-statementgroupview-property-label',
				$cloneBtn: '.wikibase-statementgroupview-property-clonebtn'
			},
			value: null,
			buildStatementListView: null,
			entityIdHtmlFormatter: null,
			htmlIdPrefix: ''
		},

		/**
		 * @property {jQuery.wikibase.statementlistview}
		 */
		statementlistview: null,

		/**
		 * @inheritdoc
		 * @protected
		 *
		 * @throws {Error} if a required option is not specified properly.
		 */
		_create: function () {
			if ( !this.options.entityIdHtmlFormatter || !this.options.buildStatementListView ) {
				throw new Error( 'Required option not specified properly' );
			}

			try {
				PARENT.prototype._create.call( this );
			} catch (e) {
				console.log('ERROR', e);
			}

			if ( this.options.value ) {
				this._updateId();
				this._updatePropertyId( this.options.value.getKey() );
				this._createPropertyLabel();
			}

			this._createStatementlistview();
		},

		/**
		 * @inheritdoc
		 */
		destroy: function () {
			if ( this.statementlistview ) {
				this.statementlistview.element.off( this.widgetName );
				this.statementlistview.destroy();
			}
			PARENT.prototype.destroy.call( this );
		},

		/**
		 * @private
		 */
		_updateId: function () {
			var propertyId = this.options.value.getKey(),
				prefix = this.options.htmlIdPrefix,
				prefixSeparator = '-';

			if ( prefix !== '' ) {
				prefix += prefixSeparator;
			}

			this.element.attr( 'id', prefix + propertyId );
		},

		/**
		 * @private
		 *
		 * @param {string} propertyId
		 */
		_updatePropertyId: function ( propertyId ) {
			this.element.data( 'property-id', propertyId );
		},

		/**
		 * @private
		 */
		_createPropertyLabel: function () {
			if ( this.$propertyLabel.contents().length > 0 ) {
				return;
			}

			var self = this,
				propertyId = this.options.value.getKey();

			this.options.entityIdHtmlFormatter.format( propertyId ).done( function ( title ) {
				self.$propertyLabel.append( title );
			} );
		},

		/**
		 * @private
		 */
		_createStatementlistview: function () {
			var self = this,
				prefix;

			var $statementlistview = this.element.find( '.wikibase-statementlistview' );

			if ( !$statementlistview.length ) {
				$statementlistview = $( '<div>' ).appendTo( this.element );
			}

			this.statementlistview = this.options.buildStatementListView(
				this.options.value ? this.options.value.getItemContainer() : new datamodel.StatementList(),
				$statementlistview
			);
			prefix = this.statementlistview.widgetEventPrefix;

			$statementlistview
			.on( prefix + 'toggleerror.' + this.widgetName, function ( event, error ) {
				self.$property.toggleClass( 'wb-error', Boolean( error ) );
			} )
			.on( prefix + 'afterstopediting.' + this.widgetName, function ( event, dropValue ) {
				self.$property.removeClass( 'wb-error wb-edit' );
				self._trigger( 'afterstopediting', null, [ dropValue ] );
			} )
			.on( prefix + 'afterstartediting.' + this.widgetName, function ( event ) {
				self.$property.addClass( 'wb-edit' );
			} )
			.on( prefix + 'afterremove.' + this.widgetName, function ( event ) {
				self.$property.removeClass( 'wb-error wb-edit' );
				self._trigger( 'afterremove' );
			} );

			//self.$cloneBtn.text('hello world');
			var _wikibasePropertyKey = self.value().getKey();


			if( _wikibasePropertyKey == "P1" || _wikibasePropertyKey == "P2"){
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

				// btn.on('click', function () {
				// 	//api call
				// 	var WIKIBASE_SYNC_URL = "http://127.0.0.1:5000/";
				// 	var full_endpoint = WIKIBASE_SYNC_URL + 'sync/' + self.wikibasePropertyValue;
				// 	$.ajax({
				// 		url: full_endpoint,
				// 		crossDomain: true,
				// 		headers: {
				// 			// "accept": "application/json",
				// 			"Access-Control-Allow-Origin": "*",
				// 			"Access-Control-Request-Headers3": "x-requested-with"
				// 		},
				// 		success: function (data) {
				// 			console.log("sync process started",data);


				// 		}
				// 	});
				// });
			}else{
				self.$cloneBtn.text('')
			}
			// console.log(JSON.stringify(self.options, null, 2));
		},

		/**
		 * Sets the widget's value or gets the widget's current value (including pending items). (The
		 * value the widget was initialized with may be retrieved via `.option( 'value' )`.)
		 *
		 * @param {datamodel.StatementGroup} [statementGroupView]
		 * @return {datamodel.StatementGroup|null|undefined}
		 */
		value: function ( statementGroupView ) {
			if ( statementGroupView !== undefined ) {
				return this.option( 'value', statementGroupView );
			}

			var statementList = this.statementlistview.value();
			if ( !statementList.length ) {
				return null;
			}
			// Use the first statement's main snak property id as the statementgroupview may have
			// been initialized without a value (as there is no initial value, the id cannot be
			// retrieved from this.options.value).
			return new datamodel.StatementGroup(
				statementList.toArray()[ 0 ].getClaim().getMainSnak().getPropertyId(),
				statementList
			);
		},

		/**
		 * @inheritdoc
		 * @protected
		 *
		 * @throws {Error} when trying to set the value passing something different than a
		 *         `datamodel.StatementGroup´ object.
		 */
		_setOption: function ( key, value ) {
			if ( key === 'value' && !!value ) {
				if ( !( value instanceof datamodel.StatementGroup ) ) {
					throw new Error( 'value needs to be a datamodel.StatementGroup instance' );
				}
				this.statementlistview.value( value.getItemContainer() );
			}

			var response = PARENT.prototype._setOption.apply( this, arguments );

			if ( key === 'disabled' ) {
				this.statementlistview.option( key, value );
			}

			return response;
		},

		/**
		 * @inheritdoc
		 */
		focus: function () {
			this.statementlistview.focus();
		},

		/**
		 * Adds a new, pending `statementview` to the encapsulated `statementlistview`.
		 *
		 * @see jQuery.wikibase.statementlistview.enterNewItem
		 *
		 * @return {Object} jQuery.Promise
		 * @return {Function} return.done
		 * @return {jQuery} return.done.$statementview
		 */
		enterNewItem: function () {
			return this.statementlistview.enterNewItem();
		}

	} );

}() );
