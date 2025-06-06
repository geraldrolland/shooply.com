class TokenIntegrityError extends Error {
    constructor(msg) {
        super(msg);
    }
}

module.exports = {TokenIntegrityError};