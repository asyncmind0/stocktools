define([ 'dojo/_base/declare',
         "dojo/dom-attr",
         "dojo/_base/event",
         "dojo/dom-construct",
         "dojo/request/xhr",
         "dojo/topic",
         "dojo/dom-style",
         "dojo/query",
         "dojo/dom",
         "dojo/on",
         "dojox/data/QueryReadStore",
         "dijit/form/TextBox",
         "dijit/form/NumberTextBox",
         "dijit/form/CurrencyTextBox",
         "dojo/currency",
         "dijit/form/DateTextBox",
         "dijit/form/Button",
         "dijit/form/CheckBox",
         "dijit/form/Form",
         "dijit/layout/ContentPane",
         "dijit/layout/BorderContainer",
         "dijit/registry",
         "dojox/grid/TreeGrid",
         "dijit/tree/ForestStoreModel",
         'dojo/data/ItemFileWriteStore',
         "dojo/date/locale",
         "dojox/widget/DialogSimple",
         "dojox/grid/cells/dijit",
         "dojo/i18n!dojo/cldr/nls/en/currency",
         "dojo/i18n!dojo/cldr/nls/en/number",
         'dojo/domReady!' ],
       function (
           declare,
           domAttr,
           event,
           domConstruct,
           xhr,
           topic,
           style,
           query,
           dom,
           on,
           QueryReadStore,
           TextBox,
           NumberTextBox,
           CurrencyTextBox,
           currency,
           DateTextBox,
           Button,
           CheckBox,
           Form,
           ContentPane,
           BorderContainer,
           registry,
           TreeGrid,
           ForestStoreModel,
           ItemFileWriteStore,
           locale,
           Dialog
       ) {
           return declare(null, {
	       title: 'Hello World',
               constructor: function(query_params){
                   console.log("constructor");
                   function formatter(){
                       var w = new Button({
                           label: "x",
                           onClick: function(event) {
                               selected = registry.byId('grid')
                                   .selection.getSelected();
                               console.log(selected);
                               console.log(selected.id);
                           }
                       });
                       w._destroyOnRemove=true;
                       return w;
                   }
                   var addTradeDialog = new Dialog({
                       title: "Add Trade",
                       style: "width: 300px",
                       href: '/portfolio/add_trade',
                       executeScripts:true
                       
                   });
                   var addTradeButton = new Button({
                       label:"Add Trade",
                       onClick: function(){
                           addTradeDialog.show();
                       }
                   }, "addTrade");
                   var removeTradeButton = new Button({
                       label:"Remove Trade",
                       onClick: function(){
                           var items = grid.selection.getSelected();
                           if(items.length){
                               dojo.forEach(items, function(selectedItem){
                                   if(selectedItem !== null){
                                       portfolioStore.deleteItem(selectedItem);
                                   } 
                               });
                           }
                           portfolioStore.save();
                           portfolioStore.close();
                       }
                   }, "removeTrade");


                   var portfolioStore = new ItemFileWriteStore(
                       {url: '/portfoliodata', });
                   portfolioStore.clearOnClose =true;
                   portfolioStore._saveEverything= function(saveCompleteCallback,
                                                            saveFailedCallback ,
                                                            newFileContentString ){
                       console.log('saveCustom');
                   };
                   
                   portfolioStore._saveCustom = function(saveCompletecallback,
                                                         saveFailedCallback){
                       console.log('saveCustom');
                   };
                   var portfolio_layout = [
                       {
                           cells: [
                               [
                                   {name: 'Portfolio', field: 'portfolio',
                                    width: '8em'},
                                   {name: 'Symbol', field: 'sym',
                                    width: '3em'},
                                   {name: 'Name', field: 'name', width: '20em'},
                                   {name: 'Sector', field: 'sector', width: '20em'},
                                   {name: 'Cost', field: 'cost',
                                    width: '5em', aggregate:'sum'},
                                   {name: 'Price', field: 'price',
                                    width: '5em',aggregate: 'sum'},
                                   {name: 'Quantity', field: 'quantity',
                                    width: '5em'},
                                   {name: 'Date', field: 'date', width: '8em'},
                                   {name: 'Fee', field: 'fee', width: '5em'},
                               ]
                           ]
                       }
                   ];
		   var treeModel = new ForestStoreModel({
		       store: portfolioStore,
		       query: { },
		       //		rootId: 'continentRoot',
		       //		rootLabel: 'Continents',
		       //childrenAttrs: ['children']
		   });

                   /*create a new grid*/
                   var grid = new TreeGrid({
                       id: 'grid',
                       treeModel: treeModel,
                       structure: portfolio_layout,
                       rowSelector: '20px',
                       summary: 'The Summary',
		       defaultOpen: true,
		       childrenAttrs: ['children', 'portfolio']
                   }, document.createElement('div'));

                   /*append the new grid to the div*/
                   domConstruct.place(grid.domNode, "gridDiv", 'last');

                   /*Call startup() to render the grid*/
                   grid.startup();
               },
               startup:function(){
               }
           });
       });
