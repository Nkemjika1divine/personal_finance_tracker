type LoginPayload = {
    email: string;
    password: string;
};

type CreateAccountPayload = {
    username: string;
    email: string;
    password: string;
}

export async function loginUser(
    fetchWithTimeout: Function, payload: LoginPayload
) {
    const formData = new URLSearchParams();
    formData.append("username", payload.email);
    formData.append("password", payload.password);

    return await fetchWithTimeout(
        "http://localhost:8000/login",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: formData.toString(),
        },
        15000
    );
}


export async function createAccount(
    fetchWithTimeout: Function, payload: CreateAccountPayload
) {
    return await fetchWithTimeout(
        "http://localhost:8000/register",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload)
        },
        15000
    );
}