
function(doc) { 
    if (doc.doc_type == 'StockDocument' && doc.url){ 
        emit(doc.url, doc); 
    }
}

