function(doc) { 
    if (doc.doc_type == 'StockDocument' && doc.symbol){ 
        emit(doc.symbol, doc); 
    }
}

