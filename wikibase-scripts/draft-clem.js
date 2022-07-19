var STATEMENT_CLASSES = ['listview-item', 'wikibase-statementgroupview', 'wb-new'];
var REFERENCE_CLASSES = ['listview-item', 'wikibase-snakview', 'wb-edit'];
var REFERENCE_INPUT_CLASSES = ['ui-suggester-input', 'ui-entityselector-input'];
var AUTOCOMPLETE_CLASSES = ['ui-ooMenu', 'ui-widget', 'ui-widget-content', 'ui-suggester-list', 'ui-entityselector-list'];

var WIKIBASE_SYNC_URL = "http://127.0.0.1:5000/";

var nextId = 0;

var lastAutocompleteElement = null;
var requestsResults = {}; // key=statementId, value=result
var lastResultStatementId = null;

(function (mw, _$) {

    function makeWikidataCall (userInput, statementId) {
        $.ajax({
            url: WIKIBASE_SYNC_URL + 'remote-wikidata-query/' + userInput,
            crossDomain: true,
            headers: {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Request-Headers3": "x-requested-with"
            },
            success: function (data) {
                requestsResults[statementId] = data;
                lastResultStatementId = statementId;
                updateAutocompleteElement(statementId);
            }
        });
    }

    function updateAutocompleteElement (statementId) {
        if (lastAutocompleteElement === null) return;

        var data = requestsResults[statementId];
        var children = Array.from(lastAutocompleteElement.children);

        if (children.length === 1 && children[0].matches('li.ui-entityselector-notfound')) {
            // No match found
            console.log('no match');
        } else {
            // At least one match found
            console.log('At least one match');
            // data.response.search.forEach(proposition => {
            //     // TODO
            // });
        }
    }

    function setLastAutocompleteElement (el) {
        // Update the global var
        lastAutocompleteElement = el;
        
        // Attach an observer to <ul> to monitor its children (detect a change)
        var acObserver = new MutationObserver(function (mutationsList) {
            mutationsList.forEach(function (mutation) {
                if (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0) {
                    // Children have been removed/added
                    if (lastResultStatementId !== null) updateAutocompleteElement(lastResultStatementId);
                }
            });
        });
        acObserver.observe(el, { childList: true });
    }

    const observer = new MutationObserver(function (mutationsList) {
        mutationsList.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (addedNode) {
                // Check for new statement block
                var isStatement = addedNode.classList && STATEMENT_CLASSES.every(function (c) { return addedNode.classList.contains(c) });
                if (isStatement) {
                    // A new statement block has been added
                    var statementId = nextId;
                    nextId += 1; 
                    var input = addedNode.querySelector('input.' + REFERENCE_INPUT_CLASSES.join('.'));
                    lastInputElement = input;
                    input.addEventListener('input', function () {
                        makeWikidataCall(input.value, statementId);
                    });
                    return;
                }

                // Check for new autocomplete element
                var isAutocomplete = addedNode.classList && AUTOCOMPLETE_CLASSES.every(function (c) { return addedNode.classList.contains(c) });
                if (isAutocomplete) {
                    // Keep track of the last one (which is the only one valid)
                    setLastAutocompleteElement(addedNode);
                    //uodate last autocomplete el with the last known result
                    if (lastResultStatementId !== null) updateAutocompleteElement(lastResultStatementId);
                }
            });
        });
    });
    observer.observe(document.body, { subtree: true, childList: true });

}(mediaWiki, jQuery));
