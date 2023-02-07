! Description:
! Elemental finite element procedures.
module m_eproc
    use linear_algebra
    use data_model
    use m_shapef
    implicit none
    
    private
    public e_get_B, e_get_C, e_get_D, e_get_K, e_get_F
    
    contains
    
    ! Description:
    ! Computes the element nodal coordinates matrix, C.
    type(t_matrix) function e_get_C(element, nodes) result(C)
        ! procedure arguments
        type(t_element), intent(in) :: element  ! finite element
        type(t_node),    intent(in) :: nodes(:) ! mesh nodes
        
        ! additional variables
        integer :: i ! loop counter
        
        ! build C
        C = new_matrix(element%n_nodes, element%n_ndofs)
        do i = 1, element%n_nodes
            C%at(i, :) = nodes(element%i_nodes(i))%coordinates(1:element%n_ndofs)
        end do
    end function
    
    ! Description:
    ! Computes the element stress-strain matrix, D.
    type(t_matrix) function e_get_D(element, section, material) result(D)
        ! procedure arguments
        type(t_element),  intent(in) :: element  ! finite element
        type(t_section),  intent(in) :: section  ! element section
        type(t_material), intent(in) :: material ! section material
        
        ! additional variables
        real :: E, nu, lambda, mu, a, b, c ! material constants
        
        ! compute material constants
        E      = material%young           ! Young's modulus
        nu     = material%poisson         ! Poisson's ratio
        lambda = E*nu/(1 + nu)/(1 - 2*nu) ! 1st Lamé modulus
        mu     = E/2/(1 + nu)             ! 2nd Lamé modulus
        a      = E/(1 - nu**2)            ! convenient constants
        b      = a*nu                     ! ...
        c      = 2*mu + lambda            ! ...
        
        ! build D
        ! working with engineering shear strain: gamma_ij = 2*epsilon_ij
        select case (section%t_section)
            case (CPS)
                D = new_matrix(3, 3)
                D%at(1, :) = [  a,   b, 0.0]
                D%at(2, :) = [  b,   a, 0.0]
                D%at(3, :) = [0.0, 0.0,  mu]
            case (CPE)
                D = new_matrix(4, 4)
                D%at(1, :) = [     c, lambda, lambda, 0.0]
                D%at(2, :) = [lambda,      c, lambda, 0.0]
                D%at(3, :) = [lambda, lambda,      c, 0.0]
                D%at(4, :) = [   0.0,    0.0,    0.0,  mu]
            case (C3D)
                D = new_matrix(6, 6)
                D%at(1, :) = [     c, lambda, lambda, 0.0, 0.0, 0.0]
                D%at(2, :) = [lambda,      c, lambda, 0.0, 0.0, 0.0]
                D%at(3, :) = [lambda, lambda,      c, 0.0, 0.0, 0.0]
                D%at(4, :) = [   0.0,    0.0,    0.0,  mu, 0.0, 0.0]
                D%at(5, :) = [   0.0,    0.0,    0.0, 0.0,  mu, 0.0]
                D%at(6, :) = [   0.0,    0.0,    0.0, 0.0, 0.0,  mu]
            case default
                error stop ERROR_UNDEFINED_SECTION_TYPE
        end select
    end function
    
    ! Description:
    ! Computes the element strain-displacement matrix, B.
    type(t_matrix) function e_get_B(element, section, nodes, i_ip, jacobian, ip_weight) result(B)
        ! procedure arguments
        type(t_element), intent(in)  :: element   ! finite element
        type(t_section), intent(in)  :: section   ! element section
        type(t_node),    intent(in)  :: nodes(:)  ! mesh nodes
        integer,         intent(in)  :: i_ip      ! integration point index
        real, optional,  intent(out) :: jacobian  ! determinant of the Jacobian matrix
        real, optional,  intent(out) :: ip_weight ! integration point weight
        
        ! additional variables
        type(t_matrix) :: Nr, Nx  ! natural and physical derivatives of shape functions
        type(t_matrix) :: C       ! nodal coordinates
        type(t_matrix) :: J, invJ ! Jacobian matrix and its inverse
        real           :: detJ    ! determinant of the Jacobian matrix
        real           :: weight  ! integration point weight
        integer        :: i, k    ! indexers
        
        ! compute physical derivatives of shape functions
        Nr   = eval_derivs(element, i_ip, weight)
        C    = e_get_C(element, nodes)
        J    = multiply(Nr, C)
        invJ = inverse(J, detJ)
        Nx   = multiply(invJ, Nr)
        
        ! assign optional output arguments
        if (present(jacobian))  jacobian  = detJ
        if (present(ip_weight)) ip_weight = weight
        
        ! build B
        select case (section%t_section)
            case (CPS)
                B = new_matrix(3, element%n_edofs)
                do i = 1, element%n_nodes
                    k = (i - 1)*element%n_ndofs + 1
                    B%at(1, k:k+1) = [Nx%at(1, i),         0.0]
                    B%at(2, k:k+1) = [        0.0, Nx%at(2, i)]
                    B%at(3, k:k+1) = [Nx%at(2, i), Nx%at(1, i)]
                end do
            case (CPE)
                B = new_matrix(4, element%n_edofs)
                do i = 1, element%n_nodes
                    k = (i - 1)*element%n_ndofs + 1
                    B%at(1, k:k+1) = [Nx%at(1, i),         0.0]
                    B%at(2, k:k+1) = [        0.0, Nx%at(2, i)]
                    B%at(3, k:k+1) = [        0.0,         0.0]
                    B%at(4, k:k+1) = [Nx%at(2, i), Nx%at(1, i)]
                end do
            case (C3D)
                B = new_matrix(6, element%n_edofs)
                do i = 1, element%n_nodes
                    k = (i - 1)*element%n_ndofs + 1
                    B%at(1, k:k+2) = [Nx%at(1, i),         0.0,         0.0]
                    B%at(2, k:k+2) = [        0.0, Nx%at(2, i),         0.0]
                    B%at(3, k:k+2) = [        0.0,         0.0, Nx%at(3, i)]
                    B%at(4, k:k+2) = [        0.0, Nx%at(3, i), Nx%at(2, i)]
                    B%at(5, k:k+2) = [Nx%at(3, i),         0.0, Nx%at(1, i)]
                    B%at(6, k:k+2) = [Nx%at(2, i), Nx%at(1, i),         0.0]
                end do
            case default
                error stop ERROR_UNDEFINED_SECTION_TYPE
        end select
    end function
    
    ! Description:
    ! Computes the element stiffness matrix, K.
    type(t_matrix) function e_get_K(element, section, material, nodes) result(K)
        ! procedure arguments
        type(t_element),  intent(in) :: element  ! finite element
        type(t_section),  intent(in) :: section  ! element section
        type(t_material), intent(in) :: material ! section material
        type(t_node),     intent(in) :: nodes(:) ! mesh nodes
        
        ! additional variables
        type(t_matrix) :: D        ! stress-strain matrix
        type(t_matrix) :: B        ! strain-displacement matrix
        real           :: jacobian ! determinant of the Jacobian matrix
        real           :: weight   ! integration point weight
        real           :: dV       ! integration factor
        integer        :: i_ip     ! integration point index
        
        ! initialize K and compute D
        K = new_matrix(element%n_edofs, element%n_edofs)
        D = e_get_D(element, section, material)
        
        ! loop over integration points
        do i_ip = 1, element%n_ips
            B  = e_get_B(element, section, nodes, i_ip, jacobian, weight)
            dV = weight*section%thickness*abs(jacobian)
            call multiply(B, multiply(D, B), K, alpha=dV, transposeA=.true.)
        end do
    end function
    
    ! Description:
    ! Computes the element internal forces vector, F.
    ! Also computes strains and stress at the integration points.
    type(t_vector) function e_get_F(element, section, material, nodes, Ua, Ub, strain, stress) result(F)
        ! procedure arguments
        type(t_element),  intent(in)  :: element  ! finite element
        type(t_section),  intent(in)  :: section  ! element section
        type(t_material), intent(in)  :: material ! section material
        type(t_node),     intent(in)  :: nodes(:) ! mesh nodes
        type(t_vector),   intent(in)  :: Ua, Ub   ! nodal displacements (global)
        type(t_matrix),   intent(out) :: strain   ! strain at the integration points
        type(t_matrix),   intent(out) :: stress   ! stress at the integration points
        
        ! additional variables
        type(t_vector) :: U        ! element nodal displacements
        type(t_matrix) :: D        ! stress-strain matrix
        type(t_matrix) :: B        ! strain-displacement matrix
        type(t_vector) :: epsilon  ! strain components
        type(t_vector) :: sigma    ! stress components
        real           :: jacobian ! determinant of the Jacobian matrix
        real           :: weight   ! integration point weight
        real           :: dV       ! integration factor
        integer        :: i_ip     ! integration point index
        integer        :: i        ! loop counter
        
        ! get nodal displacements
        U = new_vector(element%n_edofs)
        do i = 1, element%n_edofs
            if (element%dofs(i) > 0) then
                U%at(i) = Ua%at(element%dofs(i))
            else
                U%at(i) = Ub%at(abs(element%dofs(i)))
            end if
        end do
        
        ! initialize F and compute D
        F = new_vector(element%n_edofs)
        D = e_get_D(element, section, material)
        
        ! initialize strain and stress storage
        strain = new_matrix(D%n_rows, element%n_ips)
        stress = new_matrix(D%n_rows, element%n_ips)
        
        ! loop over integration points
        do i_ip = 1, element%n_ips
            B  = e_get_B(element, section, nodes, i_ip, jacobian, weight)
            dV = weight*section%thickness*abs(jacobian)
            
            ! compute strain and stress
            epsilon = multiply(B, U)
            sigma   = multiply(D, epsilon)
            
            ! store strain and stress
            strain%at(:, i_ip) = epsilon%at(:)
            stress%at(:, i_ip) = sigma%at(:)
            
            ! internal forces
            call multiply(B, sigma, F, alpha=dV, transposeA=.true.)
        end do
    end function
    
end module
