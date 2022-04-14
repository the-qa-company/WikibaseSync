/* Any JavaScript here will be loaded for all users on every page load. */
//final draftttt


var _propertyId = "";
var _propertyLabel = "";

var cloneButtonCounter = 0;
var parentIDCounter = 0;
var autoInputIDCounter = 0;
var propertyDetailArray = [];
var cloneButtonIdPrefix = 'clone_btn_';
var currentlyClickedCloneButtonId = '';
var currentBtn = null;
// var localDataLength = 1;

var _wikibasesync_base_url = "http://127.0.0.1:5000/";

function insertStyle(){
    var css = 'button.mez-appended-button:nth-child(2) {margin-top: 19px;}';
    //var css = '.wikibase-referenceview .wikibase-snaklistview-listview .wikibase-snakview-property input {position: relative !important;}';
    head = document.head || document.getElementsByTagName('head')[0];
    style = document.createElement('style');

    head.appendChild(style);

    style.type = 'text/css';
    if (style.styleSheet){
      // This is required for IE8 and below.
      style.styleSheet.cssText = css;
    } else {
      style.appendChild(document.createTextNode(css));
    }
}

(function (mw, $) {
    insertStyle()
    var _parentEl = document.getElementsByClassName('wikibase-entityview wb-item')
    var isLocallyAvailable = true
    console.log(_parentEl)

    const observer = new MutationObserver(function (mutations_list) {
        mutations_list.forEach(function (mutation) {
            mutation.addedNodes.forEach(function (added_node) {
                //console.log(Object.keys(added_node));
                var entries = Object.entries(added_node);
                var focusInput;

                if (entries.length == 2) {
                    if (entries[0][1]) {
                    // secondary wikidata autocomplete

                    $('#new .ui-entityselector-input').autocomplete({ //This is the class Name of your desired input source:
                        source: function (request, response) {
                            console.log('Request term: ' + request.term);
                            if(isLocallyAvailable == false){
                                $.ajax({
                                    // url: 'https://www.wikidata.org/w/api.php?action=wbsearchentities&search=' + request.term + '&format=json&errorformat=plaintext&language=en-gb&uselang=en-gb&type=property',
                                    url: _wikibasesync_base_url + 'remote-wikidata-query/' + request.term,
                                    // data: {term: request.term},
                                    // dataType: "json",
                                    crossDomain: true,
                                    headers: {
                                        // "accept": "application/json",
                                        "Access-Control-Allow-Origin": "*",
                                        "Access-Control-Request-Headers3": "x-requested-with"
                                    },
                                    success: function (data) {
                                        console.log(data);

                                        response($.map(data.response.search, function (item) {
                                            _propertyId = item.id;
                                            _propertyLabel = item.label;
                                            return {
                                                label: item.description,
                                                value: item.label,
                                                id: item.id
                                            }
                                        }));
                                    }
                                });
                            }else{
                                $(".ui-autocomplete").hide()
                                response = null
                                return null
                            }

                        },
                        select: function (event, ui) {
                            if(!isLocallyAvailable){
                                console.log("REMOTE OPTION SELECTED")
                                console.log($(event.target).siblings('button'));
                                $(event.target).siblings('button')[0].setAttribute('item-id', ui.item.id)
                                $(event.target).siblings('button')[0].setAttribute('item-description', ui.item.label)
                                $(event.target).siblings('button')[0].setAttribute('item-value', ui.item.value)
                            }else{
                            }

                        }
                    });


                    $('.wikibase-snakview-property input').on('keyup', function () {
                        //console.log("TYPED VALUE");
                        var typedValue = $(this).val();
                        var currentContext = $(this)
                        //check if there's data found locally
                        $.ajax({
                            url: _wikibasesync_base_url + 'local-wikibase-query/' + typedValue,
                            crossDomain: true,
                            headers: {
                                // "accept": "application/json",
                                "Access-Control-Allow-Origin": "*",
                                "Access-Control-Request-Headers3": "x-requested-with"
                            },
                            success: function (data) {
                                //console.log("RECEIVED LOCAL DATA");
                                //console.log(data.response.search.length);
                                data_length = data.response.search.length

                                if (data_length < 1) {
                                    console.log("No local data found");
                                    isLocallyAvailable = false
                                    $("ui-entityselector-notfound").hide()

                                    //console.log('No found');


                                    //focusInput = document.getElementsByClassName("ui-suggester-input ui-entityselector-input")[0].value;
                                    //console.log(focusInput);

                                    //always remove clone button while typing
                                    //var inputWithSuggestionParent = $('#new .ui-entityselector-input').parent();
                                    var appendedButton = currentContext.siblings('.mez-appended-button')
                                    if (appendedButton.length === 0 && isLocallyAvailable == false) {
                                            $("<button class='mez-appended-button' onclick='cloneAction(this)'>Clone</button>").insertAfter($(currentContext));
                                    }

                                    //if (focusInput) {
                                     //   console.log('in focus input');

                                    //}
                                } else {
                                    console.log("IN ELSE")
                                    //console.log(isLocallyAvailable)
                                    isLocallyAvailable = true

                                    var appendedButton = currentContext.siblings('.mez-appended-button')
                                    if((appendedButton.length > 0 && isLocallyAvailable) ||
                                    ( appendedButton.length > 0 && $('.wikibase-snakview-property input').val() === "")){
                                        currentContext.siblings('.mez-appended-button').remove()
                                    }
                                }
                            }
                        });
                    });
                    }
                }


            });
        });
    });

    observer.observe(document.querySelector("body"), { subtree: true, childList: true });
}(mediaWiki, jQuery));

//ui-menu-item.
//clone button clicked
function cloneAction(ele) {
    //clone action called
    console.log("Clone information: ")
    console.log(ele.getAttribute('item-id'));
    console.log(ele.getAttribute('item-description'));
    console.log(ele.getAttribute('item-value'));

    var _myPropertyId = ele.getAttribute('item-id')

    //api call
    var wikibaseSyncUrl = _wikibasesync_base_url + 'import-wikidata-item/' + _myPropertyId;
    $.ajax({
        url: wikibaseSyncUrl,
        crossDomain: true,
        headers: {
            // "accept": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Request-Headers3": "x-requested-with"
        },
        success: function (data) {
            console.log(data);
            //remove clone button
            ele.remove();
            console.log('clone button removed');

        }
    });
}

function pushNewButtonInfo(buttonId, arrayKey) {
    //add button info to array
    propertyDetailArray[arrayKey] = buttonId;

    console.log(propertyDetailArray);
}

//TODO PENDING ISSUES
//ADDING ANOTHER DIRECT INPUT FIELD CAUSES STACKING PROBLEMS
//WHEN REMOTE AUTOCOMPLETE KICKS IN, CLONE BUTTON PERSISTS AFTER ALL INPUT IS CLEARED
//EVEN WHEN DATA LENGTH IS GREATER THAN 0, AUTOCOMPLETE DISPLAYS AND THIS LEADS TO THE PROBLEM BELOW
//WHEN AUTOCOMPLETE DISPLAYS TOGETHER WITH REMOTE SUGGESTIONS,REMOTE DISPLAYS ABOVE THE LOCAL SUGGESTIONS
