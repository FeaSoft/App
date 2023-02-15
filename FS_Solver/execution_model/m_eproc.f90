! Description:
! Elemental finite element procedures.
module m_eproc
    use m_constants
    use linear_algebra
    use data_model
    use m_shapef
    implicit none
    
    private
    public e_get_B, e_get_C, e_get_D, e_get_K, e_get_M, e_get_S, e_get_Ps, e_get_Pb, e_get_F
    
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
    type(t_matrix) function e_get_D(section, material) result(D)
        ! procedure arguments
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
            case (CPE, CAX)
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
    type(t_matrix) function e_get_B(element, section, N, C, coord, i_ip, jacobian, ip_weight) result(B)
        ! procedure arguments
        type(t_element), intent(in)  :: element   ! finite element
        type(t_section), intent(in)  :: section   ! element section
        type(t_matrix),  intent(in)  :: N         ! shape functions
        type(t_matrix),  intent(in)  :: C         ! nodal coordinates matrix
        type(t_matrix),  intent(in)  :: coord     ! integration point physical coordinates
        integer,         intent(in)  :: i_ip      ! integration point index
        real, optional,  intent(out) :: jacobian  ! determinant of the Jacobian matrix
        real, optional,  intent(out) :: ip_weight ! integration point weight
        
        ! additional variables
        type(t_matrix) :: Nr, Nx  ! natural and physical derivatives of shape functions
        type(t_matrix) :: J, invJ ! Jacobian matrix and its inverse
        real           :: detJ    ! determinant of the Jacobian matrix
        real           :: weight  ! integration point weight
        integer        :: i, k    ! indexers
        
        ! compute physical derivatives of shape functions
        Nr   = eval_derivs(element, i_ip, weight)
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
            case (CAX)
                B = new_matrix(4, element%n_edofs)
                do i = 1, element%n_nodes
                    k = (i - 1)*element%n_ndofs + 1
                    B%at(1, k:k+1) = [              Nx%at(1, i),         0.0]
                    B%at(2, k:k+1) = [                      0.0, Nx%at(2, i)]
                    B%at(3, k:k+1) = [N%at(1, i)/coord%at(1, 1),         0.0]
                    B%at(4, k:k+1) = [              Nx%at(2, i), Nx%at(1, i)]
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
        type(t_matrix) :: C        ! nodal coordinates matrix
        type(t_matrix) :: B        ! strain-displacement matrix
        type(t_matrix) :: N        ! shape functions
        type(t_matrix) :: coord    ! x, y[, z] coordinates of integration point
        real           :: jacobian ! determinant of the Jacobian matrix
        real           :: weight   ! integration point weight
        real           :: dV       ! integration factor
        integer        :: i_ip     ! integration point index
        
        ! initialize K and compute D and C
        K = new_matrix(element%n_edofs, element%n_edofs)
        D = e_get_D(section, material)
        C = e_get_C(element, nodes)
        
        ! loop over integration points
        do i_ip = 1, element%n_ips
            ! evaluate shape functions and coordinates
            N = eval_functs(element, i_ip, no_imat=.true.)
            coord = multiply(N, C)
            
            ! evaluate strain-displacement matrix
            B = e_get_B(element, section, N, C, coord, i_ip, jacobian, weight)
            
            ! integration factor
            select case (section%t_section)
                case (CPS, CPE); dV = weight*abs(jacobian)*section%thickness
                case (CAX);      dV = weight*abs(jacobian)*2.0*PI*coord%at(1, 1)
                case (C3D);      dV = weight*abs(jacobian)
                case default; error stop ERROR_UNDEFINED_SECTION_TYPE
            end select
            
            ! stiffness matrix
            call multiply(B, multiply(D, B), K, alpha=dV, transposeA=.true.)
        end do
    end function
    
    ! Description:
    ! Computes the element mass matrix, M.
    type(t_matrix) function e_get_M(element, section, material, nodes) result(M)
        ! procedure arguments
        type(t_element),  intent(in) :: element  ! finite element
        type(t_section),  intent(in) :: section  ! element section
        type(t_material), intent(in) :: material ! section material
        type(t_node),     intent(in) :: nodes(:) ! mesh nodes
        
        ! additional variables
        type(t_matrix) :: C      ! nodal coordinates matrix
        type(t_matrix) :: N      ! shape functions
        type(t_matrix) :: Nr     ! natural derivatives of shape functions
        type(t_matrix) :: H      ! interpolation matrix (shape functions)
        type(t_matrix) :: J      ! Jacobian matrix
        type(t_matrix) :: coord  ! x, y[, z] coordinates of integration point
        real           :: weight ! integration point weight
        real           :: dV     ! integration factor
        integer        :: i_ip   ! integration point index
        
        ! initialize M and get C
        M = new_matrix(element%n_edofs, element%n_edofs)
        C = e_get_C(element, nodes)
        
        ! loop over integration points
        do i_ip = 1, element%n_ips
            ! evaluate shape functions and coordinates
            H = eval_functs(element, i_ip)
            N = eval_functs(element, i_ip, no_imat=.true.)
            coord = multiply(N, C)
            
            ! evaluate Jacobian matrix
            Nr = eval_derivs(element, i_ip, weight)
            J  = multiply(Nr, C)
            
            ! integration factor
            select case (section%t_section)
                case (CPS, CPE); dV = weight*abs(determinant(J))*section%thickness
                case (CAX);      dV = weight*abs(determinant(J))*2.0*PI*coord%at(1, 1)
                case (C3D);      dV = weight*abs(determinant(J))
                case default; error stop ERROR_UNDEFINED_SECTION_TYPE
            end select
            
            ! mass matrix
            call multiply(H, H, M, alpha=material%density*dV, transposeA=.true.)
            end do
    end function
    
    ! Description:
    ! Computes the element stress-stiffness matrix, S.
    type(t_matrix) function e_get_S(element, section, material, nodes, Ua, Ub) result(S)
        ! procedure arguments
        type(t_element),  intent(in) :: element  ! finite element
        type(t_section),  intent(in) :: section  ! element section
        type(t_material), intent(in) :: material ! section material
        type(t_node),     intent(in) :: nodes(:) ! mesh nodes
        type(t_vector),   intent(in) :: Ua, Ub   ! nodal displacements (global)
        
        ! additional variables
        type(t_vector) :: U             ! element nodal displacements
        type(t_matrix) :: D             ! stress-strain matrix
        type(t_matrix) :: C             ! nodal coordinates matrix
        type(t_matrix) :: B             ! strain-displacement matrix
        type(t_matrix) :: G             ! stress interpolation matrix
        type(t_matrix) :: Z             ! stress matrix
        type(t_matrix) :: N             ! shape functions
        type(t_matrix) :: Nr, Nx        ! natural and physical derivatives of shape functions
        type(t_matrix) :: Jac, invJ     ! Jacobian matrix and its inverse
        type(t_matrix) :: coord         ! x, y[, z] coordinates of integration point
        type(t_vector) :: epsilon       ! strain components
        type(t_vector) :: sigma         ! stress components
        real           :: jacobian      ! determinant of the Jacobian matrix
        real           :: weight        ! integration point weight
        real           :: dV            ! integration factor
        real           :: s11, s22, s33 ! stress components
        real           :: s23, s31, s12 ! ...
        integer        :: i_ip          ! integration point index
        integer        :: i, j, k       ! loop counters
        
        ! initialize S and compute D and C
        S = new_matrix(element%n_edofs, element%n_edofs)
        D = e_get_D(section, material)
        C = e_get_C(element, nodes)
        
        ! get nodal displacements
        U = new_vector(element%n_edofs)
        do i = 1, element%n_edofs
            if (element%dofs(i) > 0) then
                U%at(i) = Ua%at(element%dofs(i))
            else
                U%at(i) = Ub%at(abs(element%dofs(i)))
            end if
        end do
        
        ! add displacements to nodal coordinates (updated Lagrange approach)
        do i = 1, element%n_nodes
            do j = 1, element%n_ndofs
                k = (i - 1)*element%n_ndofs + j
                C%at(i, j) = C%at(i, j) + U%at(k)
            end do
        end do
        
        ! loop over integration points
        do i_ip = 1, element%n_ips
            ! evaluate shape functions and coordinates
            N = eval_functs(element, i_ip, no_imat=.true.)
            coord = multiply(N, C)
            
            ! evaluate physical derivatives of shape functions
            Nr   = eval_derivs(element, i_ip, weight)
            Jac  = multiply(Nr, C)
            invJ = inverse(Jac)
            Nx   = multiply(invJ, Nr)
            
            ! evaluate strain-displacement matrix
            B = e_get_B(element, section, N, C, coord, i_ip, jacobian, weight)
            
            ! compute strain and stress
            epsilon = multiply(B, U)
            sigma   = multiply(D, epsilon)
            
            ! build G
            G = new_matrix(9, element%n_edofs)
            do i = 1, element%n_nodes
                do j = 1, element%n_ndofs
                    do k = 1, element%n_ndofs
                        G%at((k - 1)*3 + j, (i - 1)*element%n_ndofs + j) = Nx%at(k, i)
                    end do
                end do
            end do
            
            ! build Z
            select case (section%t_section)
                case (CPS)
                    s11 = sigma%at(1)
                    s22 = sigma%at(2)
                    s33 = 0.0
                    s23 = 0.0
                    s31 = 0.0
                    s12 = sigma%at(3)
                case (CPE, CAX)
                    s11 = sigma%at(1)
                    s22 = sigma%at(2)
                    s33 = sigma%at(3)
                    s23 = 0.0
                    s31 = 0.0
                    s12 = sigma%at(4)
                case (C3D)
                    s11 = sigma%at(1)
                    s22 = sigma%at(2)
                    s33 = sigma%at(3)
                    s23 = sigma%at(4)
                    s31 = sigma%at(5)
                    s12 = sigma%at(6)
                case default
                    error stop ERROR_UNDEFINED_SECTION_TYPE
            end select
            Z = new_matrix(9, 9)
            Z%at(1, :) = [s11, 0.0, 0.0, s12, 0.0, 0.0, s31, 0.0, 0.0]
            Z%at(2, :) = [0.0, s11, 0.0, 0.0, s12, 0.0, 0.0, s31, 0.0]
            Z%at(3, :) = [0.0, 0.0, s11, 0.0, 0.0, s12, 0.0, 0.0, s31]
            Z%at(4, :) = [s12, 0.0, 0.0, s22, 0.0, 0.0, s23, 0.0, 0.0]
            Z%at(5, :) = [0.0, s12, 0.0, 0.0, s22, 0.0, 0.0, s23, 0.0]
            Z%at(6, :) = [0.0, 0.0, s12, 0.0, 0.0, s22, 0.0, 0.0, s23]
            Z%at(7, :) = [s31, 0.0, 0.0, s23, 0.0, 0.0, s33, 0.0, 0.0]
            Z%at(8, :) = [0.0, s31, 0.0, 0.0, s23, 0.0, 0.0, s33, 0.0]
            Z%at(9, :) = [0.0, 0.0, s31, 0.0, 0.0, s23, 0.0, 0.0, s33]
            
            ! integration factor
            select case (section%t_section)
                case (CPS, CPE); dV = weight*abs(jacobian)*section%thickness
                case (CAX);      dV = weight*abs(jacobian)*2.0*PI*coord%at(1, 1)
                case (C3D);      dV = weight*abs(jacobian)
                case default; error stop ERROR_UNDEFINED_SECTION_TYPE
            end select
            
            ! stress-stiffness matrix
            call multiply(G, multiply(Z, G), S, alpha=dV, transposeA=.true.)
        end do
    end function
    
    ! Description:
    ! Computes the element surface loads vector, Ps.
    type(t_vector) function e_get_Ps(surface, element, F, A) result(Ps)
        ! procedure arguments
        type(t_surface), intent(in) :: surface ! element surface
        type(t_element), intent(in) :: element ! finite element
        type(t_vector),  intent(in) :: F       ! body load components
        real,            intent(in) :: A       ! surface area
        
        ! additional variables
        integer :: i, j ! indices
        
        ! initialize Ps
        Ps = new_vector(element%n_edofs)
        
        ! simplified approach
        do i = 1, surface%n_nodes
            j = (surface%i_nodes(i) - 1)*element%n_ndofs + 1
            Ps%at(j:j+element%n_ndofs-1) = A*F%at(:)/surface%n_nodes
        end do
    end function
    
    ! Description:
    ! Computes the element body loads vector, Pb.
    type(t_vector) function e_get_Pb(element, section, nodes, F) result(Pb)
        ! procedure arguments
        type(t_element), intent(in) :: element  ! finite element
        type(t_section), intent(in) :: section  ! element section
        type(t_node),    intent(in) :: nodes(:) ! mesh nodes
        type(t_vector),  intent(in) :: F        ! body load components
        
        ! additional variables
        type(t_matrix) :: C      ! nodal coordinates matrix
        type(t_matrix) :: N      ! shape functions
        type(t_matrix) :: Nr     ! natural derivatives of shape functions
        type(t_matrix) :: H      ! interpolation matrix (shape functions)
        type(t_matrix) :: J      ! Jacobian matrix
        type(t_matrix) :: coord  ! x, y[, z] coordinates of integration point
        real           :: weight ! integration point weight
        real           :: dV     ! integration factor
        integer        :: i_ip   ! integration point index
        
        ! initialize Pb and get C
        Pb = new_vector(element%n_edofs)
        C  = e_get_C(element, nodes)
        
        ! loop over integration points
        do i_ip = 1, element%n_ips
            ! evaluate shape functions and coordinates
            H = eval_functs(element, i_ip)
            N = eval_functs(element, i_ip, no_imat=.true.)
            coord = multiply(N, C)
            
            ! evaluate Jacobian matrix
            Nr = eval_derivs(element, i_ip, weight)
            J  = multiply(Nr, C)
            
            ! integration factor
            select case (section%t_section)
                case (CPS, CPE); dV = weight*abs(determinant(J))*section%thickness
                case (CAX);      dV = weight*abs(determinant(J))*2.0*PI*coord%at(1, 1)
                case (C3D);      dV = weight*abs(determinant(J))
                case default; error stop ERROR_UNDEFINED_SECTION_TYPE
            end select
            
            ! body forces
            call multiply(H, F, Pb, alpha=dV, transposeA=.true.)
        end do
    end function
    
    ! Description:
    ! Computes the element internal forces vector, F.
    ! Also computes strains and stresses at the integration points.
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
        type(t_matrix) :: C        ! nodal coordinates matrix
        type(t_matrix) :: B        ! strain-displacement matrix
        type(t_matrix) :: N        ! shape functions
        type(t_vector) :: epsilon  ! strain components
        type(t_vector) :: sigma    ! stress components
        type(t_matrix) :: coord    ! x, y[, z] coordinates of integration point
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
        
        ! initialize F and compute D and C
        F = new_vector(element%n_edofs)
        D = e_get_D(section, material)
        C = e_get_C(element, nodes)
        
        ! initialize strain and stress storage
        strain = new_matrix(D%n_rows, element%n_ips)
        stress = new_matrix(D%n_rows, element%n_ips)
        
        ! loop over integration points
        do i_ip = 1, element%n_ips
            ! evaluate shape functions and coordinates
            N = eval_functs(element, i_ip, no_imat=.true.)
            coord = multiply(N, C)
            
            ! evaluate strain-displacement matrix
            B = e_get_B(element, section, N, C, coord, i_ip, jacobian, weight)
            
            ! integration factor
            select case (section%t_section)
                case (CPS, CPE); dV = weight*abs(jacobian)*section%thickness
                case (CAX);      dV = weight*abs(jacobian)*2.0*PI*coord%at(1, 1)
                case (C3D);      dV = weight*abs(jacobian)
                case default; error stop ERROR_UNDEFINED_SECTION_TYPE
            end select
            
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
