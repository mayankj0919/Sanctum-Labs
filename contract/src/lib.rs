#![no_std]
use soroban_sdk::{contract, contractimpl, Env, Symbol, String, symbol_short};

#[contract]
pub struct SanctumHashContract;

#[contractimpl]
impl SanctumHashContract {
    /// Stores the SHA256 report hash (hex string) for a given project_id.
    pub fn store_hash(env: Env, project_id: Symbol, hash: String) {
        env.storage().persistent().set(&project_id, &hash);
    }

    /// Retrieves the stored hash string for a given project_id.
    pub fn get_hash(env: Env, project_id: Symbol) -> String {
        env.storage()
            .persistent()
            .get(&project_id)
            .expect("No hash found for this project_id")
    }
}

#[cfg(test)]
mod test {
    use super::*;
    use soroban_sdk::Env;

    #[test]
    fn test_store_and_get() {
        let env = Env::default();
        let contract_id = env.register_contract(None, SanctumHashContract);
        let client = SanctumHashContractClient::new(&env, &contract_id);

        let project_id = symbol_short!("PRJ_001");
        let hash = String::from_str(
            &env,
            "980e1627cc2592f9c5e6d8755303869f884a0ad82e0d71db3427bfd78285f03f",
        );

        client.store_hash(&project_id, &hash);
        assert_eq!(client.get_hash(&project_id), hash);
    }
}
