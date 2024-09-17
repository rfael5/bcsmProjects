import { NavLink } from "react-router-dom";

const NavBar = () => {
    return (
        <nav className="d-flex mt-3">
            <ul>
                <button className="btn btn-secondary me-3">
                    <NavLink to="/adm-horas" style={{textDecoration:'none'}} className="text-light">Controle de horas</NavLink>
                </button>
                <button className="btn btn-secondary">
                    <NavLink to="/" style={{textDecoration:'none'}} className="text-light">Listagem</NavLink>
                </button>

                <button className="btn btn-secondary">
                    <NavLink to="/importar-horas" style={{textDecoration:'none'}} className="text-light">Importar horas</NavLink>
                </button>
            </ul>
        </nav>
    )
}

export default NavBar;