/**
 * @param {object} obj
 * @returns {string}
 */
function stringify(obj) {
  return JSON.stringify(obj, (_key, value) =>
    value instanceof Set ? [...value] : value,
  );
}

/**
 * @returns {{ [note: string]: boolean }}
 */
function makeNotesState() {
  return Object.fromEntries(
    [...Array(24).keys()].map((n) => [2 ** (24 - n - 1), false]),
  );
}

/**
 * @param {{ [note: string]: boolean }} selectedNotes
 * @returns {number}
 */
function calculateBinaryRepr(selectedNotes) {
  let result = 0;
  for (const note of Object.keys(selectedNotes)) {
    if (selectedNotes[note]) {
      result += parseInt(note);
    }
  }
  return result;
}

/**
 * @param {number} intervalsBinary
 * @param { string[] } notesNotations
 * @param {{ [maqam: string]: number[] }} maqamat
 * @returns {{ [maqam: string]: Set<string> }}
 */
function findMatchingMaqamat(intervalsBinary, notesNotations, maqamat) {
  /** @type {{ [maqam: string]: Set<string> }} */
  const results = Object.fromEntries(
    Object.keys(maqamat).map((m) => [m, new Set()]),
  );
  for (const maqamName of Object.keys(maqamat)) {
    maqamat[maqamName].forEach((variation) => {
      /** @type {number?} */
      let adjusted = null;
      notesNotations.forEach((note) => {
        if (adjusted !== null) {
          const carry = adjusted & (2 ** 23);
          adjusted = ((adjusted - carry) << 1) + (carry == 0 ? 0 : 1);
        } else {
          adjusted = variation;
        }
        if ((adjusted | intervalsBinary) == adjusted) {
          results[maqamName].add(note);
        }
      });
    });
  }
  return results;
}

/**
 * @param {{[note: string]: boolean}} notes
 * @returns {number}
 */
function selectedAmount(notes) {
  return Object.keys(notes).filter((note) => notes[note]).length;
}
