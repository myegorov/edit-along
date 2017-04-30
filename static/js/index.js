window.onload = function() {
  let textarea = document.getElementById('textarea');
  textarea.focus();

  let observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      // let rec = {
      //   mutation: mutation,
      //   el: mutation.target,
      //   val: mutation.target.textContent,
      //   oldVal: mutation.oldValue
      // };
      // console.log(rec);

      console.log(textarea.innerText);
    });
  });

  let observerOptions = {
    subtree: true,
    characterData: true
  };

  observer.observe(textarea, observerOptions);
}
