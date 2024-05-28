
function printPage() {
    window.print();
}

function printDiv(divName) {
    const printContents = document.getElementById(divName).innerHTML;
    const originalContents = document.body.innerHTML;
    document.body.innerHTML = printContents;
    window.print();
    document.body.innerHTML = originalContents;
}

function clear_form(fieldsToClear=['car_no', 'p_space']){
    let form=document.getElementById('form_filter');
    if (form) {
      let inputs = form.getElementsByTagName('input');
      for (let i = 0; i < inputs.length; i++) {
        if (fieldsToClear.includes(inputs[i].name)) {
          inputs[i].value = '';
        }
      }
     }
}

function goBackOnHistory(element){
    if (window.history && window.history.length > 1) {
      window.history.back();
    }else{
      window.location.href = '/';
    }
}