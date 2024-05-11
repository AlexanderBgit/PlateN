function clear_form(){
    let form=document.getElementById('form_filter');
    if (form) {
      let inputs = form.getElementsByTagName('input');
      let fieldsToClear = ['car_no', 'r_id'];
      for (let i = 0; i < inputs.length; i++) {
        if (fieldsToClear.includes(inputs[i].name)) {
          inputs[i].value = '';
        }
      }
     }
}