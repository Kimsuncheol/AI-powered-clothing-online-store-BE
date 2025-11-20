# AI-powered-clothing-online-store-BE

## Backend/Auth Prompt Addenda

### FR-BE-02 – Sign Up
- Sign up input includes `email`, `password`, `confirm_password`, and `role` (buyer/seller/admin).
- Password must meet frontend rules (length, upper/lowercase, digit, special char) and match confirmation before hashing/storing.

### NFR-BE-01 – Security
- Password constraints are enforced on both FE and BE; backend is source of truth if FE is bypassed.
- Backend mirrors FE password rules and ensures `password === confirm_password`; never persist `confirm_password`.
- Email format and max-length constraints enforced FE/BE; backend also checks email uniqueness.
