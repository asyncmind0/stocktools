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
         "dijit/form/Form",
         "dijit/form/FilteringSelect",
         "dojo/store/Memory",
         "dijit/layout/ContentPane",
         "dijit/layout/BorderContainer",
         "dijit/registry",
         'dojo/data/ItemFileWriteStore',
         "dojo/date/locale",
         "dojo/text!./_TradeForm.html",
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
           Form,
           FilteringSelect,
           MemoryStore,
           ContentPane,
           BorderContainer,
           registry,
           ItemFileWriteStore,
           locale,
           template
       ) {
           function get_price(sym, date){
               url = '/portfolio/get_price?sym='+sym;
               if(date){
                   var format = {selector: 'date',
                                 datePattern: 'yyyyMMdd',
                                 locale: 'en-au'};
                   url += '&date='+ locale.format(date, format);
               }
               xhr.get(url,
                       {handleAs: 'json'})
                   .then(function(data){
                       console.log(data);
                       registry.byId('price')
                           .set('value', data.sym[sym]);
                       if(date){
                       }
                       
                   },function(data){
                       console.log(data);
                   });
           }
           return declare("stocktools.TradeForm", Form, {
	       title: 'Hello World trade',
	       templateString: template,
               submitButton: new Button({
                   type: "submit",
                   label: "ready!"
               }),
               domNode: domConstruct.create('div'),
               widgetsInTemplate: true,
               constructor: function(args) {
                   args.action="/portfolio/add";
                   args.method="POST";
                   args.encType="multipart/form-data";
                   declare.safeMixin(this, args);
               },
               onSubmit: function() {
                   if(this.validate()){
                       return true;
                   }else{
                       return false;
                   }
               },
               currencyFormat:  currency.format(
                   54775.53, {locale: 'en-au', currency: "AUD"}),
               postCreate: function() {
                   this.symbolFilteringSelect= new FilteringSelect({
                       name: "sym",
                       value: "" /* no or empty value! */,
                       placeHolder: "Symbol",
                       uppercase: true,
                       required: true,
                       labelAttr: 'name',
                       store: new ItemFileWriteStore({url: '/symboldata'}),
                       searchAttr: 'sym',
		       style: "width: 160px",
                       onChange:function(value){
                           get_price(this.attr('displayedValue'));
                       }
                   }, this.sym);
                   this.xsrfTextBox= new TextBox({
                       name: '_xsrf',
                       type: 'hidden',
                       required: true,
                       value: this._xsrfToken
                   }, this._xsrf);
                   
                   this.costTextBox= new CurrencyTextBox({
                       id:"cost",
                       name:"cost",
                       value: 0.0,
                       lang: 'en-au',
                       currency: "AUD",
                       placeHolder: "cost",
                       required: true,
                       invalidMessage: "Invalid amount.  Example: "
                           + this.currencyFormat
                   }, this.cost);
                   this.priceTextBox= new CurrencyTextBox({
                       id:"price",
                       name:"price",
                       value: 0.0,
                       lang: 'en-au',
                       currency: "AUD",
                       readOnly: true,
                       required: true,
                       invalidMessage: "Invalid amount.  Example: "
                           + this.currencyFormat
                   }, this.price);

                   this.quantityTextBox= new NumberTextBox({
                       name: "quantity",
                       constraints: {pattern: "#####"},
                       required: true,
                       onChange:function(value){
                           var price = registry.byId('price').get('value');
                           if(price){
                               registry.byId('cost')
                                   .set('value', value*price);
                           }
                       }
                   }, this.quantity);

                   this.dateTextBox= new DateTextBox({
                       value: new Date(),
                       name: "date",
                       onChange:function(value){
                           var sym = registry.byId('sym').get('value');
                           get_price(sym, value);
                       }
                   }, this.date);

                   this.feeTextBox= new CurrencyTextBox({
                       name:"fee",
                       value: 0.0,
                       lang: 'en-au',
                       currency: "AUD",
                       required: true,
                       invalidMessage: "Invalid amount.  Example: "
                           + self.currencyFormat
                   }, this.fee);

                   this.submitButton= new Button({
                       label:"Add",
                       type: 'submit',
                       /*onClick: function(){
                         this.submit();
                         }*/
                   }, this.submit);
               },

           });
       });
