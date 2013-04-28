function(doc) { 
    if (doc.doc_type == 'StockDocument'){ 
        emit(doc._id, doc); 
    }
}
