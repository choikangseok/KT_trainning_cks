var list = [0,1,2,3,4,5,6,7,8,9];
var number = [];

var log='-------------------------------<br>';


if (confirm('야구 게임을 시작하시겠습니까?') == true){
    for(var i = 0; i < 3; i++) {
        var select = Math.floor(Math.random() * list.length);
    number[i] = list.splice(select,1)[0];
    }

    var count = 0;
    var strike = 0;
    var ball = 0;
    var error = 0;

    alert("답 :"+number[0]+number[1]+number[2]);

    while (count < 3) {
    var input = prompt('숫자를 입력하세요'); 
    log = log.concat('숫자를 입력하세요 : '+input+"<br>");
    var inputArray = input.split(''); 
    console.log(input);

    strike = 0; 
    ball = 0;
    count++;
    
    if(input === 'undefined') break; //취소 눌렀을시 종료;

    
    // 입력받은 숫자를 비교분석하는 부분
    for (var j = 0; j < 3; j++) {
        for (var k = 0; k < 3; k++) {
        if (number[j] == inputArray[k]) {
            if (j === k) {
            strike++;
            } else {
            ball++;
            }
            break;
        }
        }
    }
    

    // 결과를 표시하는 부분
    if (strike === 3) {
        alert('홈런!!! ' + (count) + '번 만에 맞추셨습니다');
        log = log.concat('홈런!!! ' + (count) + '번 만에 맞추셨습니다'+"<br>");
        break;
    } else if (count >= 3) {
        alert('시도 횟수를 초과하셨습니다.');
        log = log.concat('시도 횟수를 초과하셨습니다.'+"<br>");
    } else {
        alert(inputArray.join('') + ': ' + strike + '스트라이크 ' + ball + '볼');
        log = log.concat(inputArray.join('') + ': ' + strike + '스트라이크 ' + ball + '볼'+"<br>");
    }
    }

    log = log.replace(",","");
    // alert(log);
    log = log.concat('-------------------------------<br><br>');
    document.getElementById("text1").value = log;
}
