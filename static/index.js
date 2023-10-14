/**
 * @typedef {{ [maqam: string]: number[] }} MaqamatVariations
 * @typedef {{ [maqam: string]: Set<string> }} MatchedMaqamat
 * @typedef {{ [note: string]: boolean }} SelectedNotes
 */

/**
 * @param {string[]} notesNotations
 * @param {MaqamatVariations} maqamat
 */
function makeState(notesNotations, maqamat) {
  return {
    /** @type {SelectedNotes} */
    notes: Object.fromEntries(
      [...Array(24).keys()].map((n) => [2 ** (24 - n - 1), false]),
    ),
    /** @type {MatchedMaqamat} */
    matches: {},
    refreshMatches() {
      this.matches = findMatchingMaqamat(
        calculateBinaryRepr(this.notes),
        notesNotations,
        maqamat,
      );
    },
    /**
     * @param {number} i
     * @param {"quarter" | "equal"} type
     */
    toggleNote(i, type) {
      this.notes[i] = !this.notes[i];
      if (this.notes[i]) {
        if (type == "equal") this.notes[i * 2] = false;
        else if (type == "quarter") this.notes[i / 2] = false;
      }
      this.refreshMatches();
    },
    /**
     * @param {number} i
     * @param {"black" | "white"} color
     */
    getNoteBgClass(i, color) {
      if (this.notes[i]) {
        return "note-selected-bg";
      } else if (this.notes[i * 2]) {
        return "note-quarterly-selected-bg";
      } else {
        return `bg-${color}`;
      }
    },
  };
}

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
 * @param {SelectedNotes} selectedNotes
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
 * @param {string[]} notesNotations
 * @param {MaqamatVariations} maqamat
 * @returns {MatchedMaqamat}
 */
function findMatchingMaqamat(intervalsBinary, notesNotations, maqamat) {
  /** @type {MatchedMaqamat} */
  const results = Object.fromEntries(
    Object.keys(maqamat).map((m) => [m, new Set()]),
  );

  for (const maqamName of Object.keys(maqamat)) {
    maqamat[maqamName].forEach((variation) => {
      /** @type {number?} */
      let adjusted = null;
      notesNotations.forEach((note, i) => {
        if (adjusted !== null) {
          const carry = adjusted & 1;
          adjusted = ((adjusted - carry) >> 1) + (carry == 0 ? 0 : (2 ** 23));
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
 * @param {SelectedNotes} selectedNotes
 * @returns {number}
 */
function selectedAmount(selectedNotes) {
  const allNotes = Object.keys(selectedNotes);
  return allNotes.filter((note) => selectedNotes[note]).length;
}
