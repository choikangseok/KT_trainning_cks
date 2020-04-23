function defSearch(frm){
    if(frm.keyWord.value ==""){
        alert("검색 단어를 입력하세요.");
        frm.keyWord.focus();
        return;
    }
    frm.submit();  
}