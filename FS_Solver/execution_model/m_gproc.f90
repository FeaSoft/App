! Description:
! Global finite element procedures.
module m_gproc
    use linear_algebra
    use data_model
    use m_shapef
    use m_eproc
    implicit none
    
    private
    public g_get_K, g_get_F, g_get_Ub, g_add_Pc, extra_strain, extra_stress, extrapolate, average, convert_vector
    
    contains
    
    ! Description:
    ! Computes the global stiffness matrix, Kaa and Kab.
    subroutine g_get_K(n_adofs, n_idofs, mesh, sections, materials, Kaa, Kab)
        ! procedure arguments
        integer,          intent(in)  :: n_adofs      ! number of active degrees of freedom
        integer,          intent(in)  :: n_idofs      ! number of inactive degrees of freedom
        type(t_mesh),     intent(in)  :: mesh         ! finite element mesh
        type(t_section),  intent(in)  :: sections(:)  ! sections
        type(t_material), intent(in)  :: materials(:) ! materials
        type(t_sparse),   intent(out) :: Kaa, Kab     ! global stiffness matrix
        
        ! additional variables
        type(t_matrix), allocatable :: Ks(:)    ! element stiffness matrices
        type(t_element)             :: element  ! finite element
        type(t_section)             :: section  ! element section
        type(t_material)            :: material ! section material
        integer                     :: i        ! loop counter
        
        ! compute element stiffness matrices first (giving a chance for this loop to be parallelized)
        allocate(Ks(mesh%n_elements))
        do i = 1, mesh%n_elements
            element  = mesh%elements(i)
            section  = sections(element%i_section)
            material = materials(section%i_material)
            Ks(i)    = e_get_K(element, section, material, mesh%nodes)
        end do
        
        ! build global matrix
        call local_to_global_matrix(n_adofs, n_idofs, mesh%n_elements, mesh%elements, Ks, Kaa, Kab)
        
        ! deallocate Ks
        if (allocated(Ks)) deallocate(Ks)
    end subroutine
    
    ! Description:
    ! Computes the global internal forces vector, F.
    ! Also computes strains and stress at the integration points.
    subroutine g_get_F(n_adofs, n_idofs, mesh, sections, materials, Ua, Ub, Fa, Fb, strain, stress)
        ! procedure arguments
        integer,          intent(in)    :: n_adofs      ! number of active degrees of freedom
        integer,          intent(in)    :: n_idofs      ! number of inactive degrees of freedom
        type(t_mesh),     intent(in)    :: mesh         ! finite element mesh
        type(t_section),  intent(in)    :: sections(:)  ! sections
        type(t_material), intent(in)    :: materials(:) ! materials
        type(t_vector),   intent(in)    :: Ua, Ub       ! nodal displacements (global)
        type(t_vector),   intent(out)   :: Fa, Fb       ! global internal forces vector
        type(t_matrix),   intent(inout) :: strain(:)    ! strain at the integration points
        type(t_matrix),   intent(inout) :: stress(:)    ! stress at the integration points
        
        ! additional variables
        type(t_vector), allocatable :: Fs(:)    ! element internal forces vectors
        type(t_element)             :: element  ! finite element
        type(t_section)             :: section  ! element section
        type(t_material)            :: material ! section material
        integer                     :: i        ! loop counter
        
        ! compute element internal forces vectors first (giving a chance for this loop to be parallelized)
        allocate(Fs(mesh%n_elements))
        do i = 1, mesh%n_elements
            element  = mesh%elements(i)
            section  = sections(element%i_section)
            material = materials(section%i_material)
            Fs(i)   = e_get_F(element, section, material, mesh%nodes, Ua, Ub, strain(i), stress(i))
        end do
        
        ! build global vector
        call local_to_global_vector(n_adofs, n_idofs, mesh%n_elements, mesh%elements, Fs, Fa, Fb)
        
        ! deallocate Fs
        if (allocated(Fs)) deallocate(Fs)
    end subroutine
    
    ! Description:
    ! Returns the known displacements vector, Ub.
    type(t_vector) function g_get_Ub(m_space, n_idofs, n_boundaries, nodes, boundaries, nsets) result(Ub)
        ! procedure arguments
        integer,          intent(in) :: m_space       ! modeling space
        integer,          intent(in) :: n_idofs       ! number of inactive degrees of freedom
        integer,          intent(in) :: n_boundaries  ! number of boundary conditions
        type(t_node),     intent(in) :: nodes(:)      ! mesh nodes
        type(t_boundary), intent(in) :: boundaries(:) ! boundary conditions
        type(t_nset),     intent(in) :: nsets(:)      ! node sets
        
        ! additional variables
        type(t_boundary) :: boundary ! boundary condition
        type(t_nset)     :: nset     ! node set
        type(t_node)     :: node     ! mesh node
        integer          :: i, j, k  ! loop counters
        
        ! initialize vector
        Ub = new_vector(n_idofs)
        
        ! build vector
        do i = 1, n_boundaries
            boundary = boundaries(i)
            nset     = nsets(boundary%i_nset)
            do j = 1, nset%n_nodes
                node = nodes(nset%i_nodes(j))
                do k = 1, m_space
                    if (node%dofs(k) < 0) then
                        Ub%at(abs(node%dofs(k))) = boundary%components(k)
                    end if
                end do
            end do
        end do
    end function
    
    ! Description:
    ! Adds the global concentrated loads vector, Pc, to the equivalent nodal loads vector, Pa.
    subroutine g_add_Pc(m_space, n_cloads, nodes, cloads, nsets, Pa)
        ! procedure arguments
        integer,        intent(in)    :: m_space   ! modeling space
        integer,        intent(in)    :: n_cloads  ! number of concentrated loads
        type(t_node),   intent(in)    :: nodes(:)  ! mesh nodes
        type(t_cload),  intent(in)    :: cloads(:) ! concentrated loads
        type(t_nset),   intent(in)    :: nsets(:)  ! node sets
        type(t_vector), intent(inout) :: Pa        ! equivalent nodal loads vector
        
        ! additional variables
        type(t_cload) :: cload   ! concentrated load
        type(t_nset)  :: nset    ! node set
        type(t_node)  :: node    ! mesh node
        integer       :: i, j, k ! loop counters
        
        ! add contributions to vector
        do i = 1, n_cloads
            cload = cloads(i)
            nset  = nsets(cload%i_nset)
            do j = 1, nset%n_nodes
                node = nodes(nset%i_nodes(j))
                do k = 1, m_space
                    if (node%dofs(k) > 0) then
                        Pa%at(node%dofs(k)) = Pa%at(node%dofs(k)) + cload%components(k)
                    end if
                end do
            end do
        end do
    end subroutine
    
    ! Description:
    ! Computes additional strain measures (principal strains).
    subroutine extra_strain(strain, extra)
        ! procedure arguments
        type(t_matrix), intent(in)    :: strain(:) ! strain at the integration points (basic components)
        type(t_matrix), intent(inout) :: extra(:)  ! strain at the integration points (with extra strain measures)
        
        ! additional variables
        type(t_matrix) :: matrix                       ! matrix representation of tensor
        type(t_vector) :: eigenvalues                  ! eigenvalues in ascending order
        real           :: e11, e22, e33, e23, e31, e12 ! strain components
        real           :: e1, e2, e3, eMajor           ! principal strains
        integer        :: i, j                         ! loop counters
        
        ! compute extra strain components
        do i = 1, size(strain)                          ! for each element
            extra(i) = new_matrix(10, strain(i)%n_cols) ! e11, e22, e33, e23, e31, e12, e1, e2, e3, eMajor
            do j = 1, strain(i)%n_cols                  ! for each integration point
                ! get individual components
                select case (strain(i)%n_rows)
                    ! plane stress
                    case (3)
                        e11 = strain(i)%at(1, j)
                        e22 = strain(i)%at(2, j)
                        e33 = 0.0
                        e23 = 0.0
                        e31 = 0.0
                        e12 = strain(i)%at(3, j)
                    ! plane strain
                    case (4)
                        e11 = strain(i)%at(1, j)
                        e22 = strain(i)%at(2, j)
                        e33 = strain(i)%at(3, j)
                        e23 = 0.0
                        e31 = 0.0
                        e12 = strain(i)%at(4, j)
                    ! general case
                    case (6)
                        e11 = strain(i)%at(1, j)
                        e22 = strain(i)%at(2, j)
                        e33 = strain(i)%at(3, j)
                        e23 = strain(i)%at(4, j)
                        e31 = strain(i)%at(5, j)
                        e12 = strain(i)%at(6, j)
                    ! otherwise
                    case default
                        error stop ERROR_UNDEFINED_SECTION_TYPE
                end select
                
                ! build matrix
                matrix = new_matrix(3, 3)
                matrix%at(1, :) = [e11,     e12/2.0, e31/2.0]
                matrix%at(2, :) = [e12/2.0, e22,     e23/2.0]
                matrix%at(3, :) = [e31/2.0, e23/2.0, e33    ]
                
                ! compute principal strains
                eigenvalues = eigen(matrix)
                e1          = eigenvalues%at(3)
                e2          = eigenvalues%at(2)
                e3          = eigenvalues%at(1)
                eMajor      = eigenvalues%at(maxloc(abs(eigenvalues%at(:)), dim=1))
                
                ! store results
                extra(i)%at(:, j) = [e11, e22, e33, e23, e31, e12, e1, e2, e3, eMajor]
            end do
        end do
    end subroutine
    
    ! Description:
    ! Computes additional stress measures (principal stresses and equivalent stresses).
    subroutine extra_stress(stress, extra)
        ! procedure arguments
        type(t_matrix), intent(in)    :: stress(:) ! stress at the integration points (basic components)
        type(t_matrix), intent(inout) :: extra(:)  ! stress at the integration points (with extra stress measures)
        
        ! additional variables
        type(t_matrix) :: matrix                       ! matrix representation of tensor
        type(t_vector) :: eigenvalues                  ! eigenvalues in ascending order
        real           :: s11, s22, s33, s23, s31, s12 ! stress components
        real           :: s1, s2, s3, sMajor           ! principal stresses
        real           :: sTresca, sMises, sPress      ! equivalent stresses
        integer        :: i, j                         ! loop counters
        
        ! compute extra stress components
        do i = 1, size(stress)                          ! for each element
            extra(i) = new_matrix(13, stress(i)%n_cols) ! s11, s22, s33, s23, s31, s12, s1, s2, s3, sMajor, sTresca, sMises, sPress
            do j = 1, stress(i)%n_cols                  ! for each integration point
                ! get individual components
                select case (stress(i)%n_rows)
                    ! plane stress
                    case (3)
                        s11 = stress(i)%at(1, j)
                        s22 = stress(i)%at(2, j)
                        s33 = 0.0
                        s23 = 0.0
                        s31 = 0.0
                        s12 = stress(i)%at(3, j)
                    ! plane strain
                    case (4)
                        s11 = stress(i)%at(1, j)
                        s22 = stress(i)%at(2, j)
                        s33 = stress(i)%at(3, j)
                        s23 = 0.0
                        s31 = 0.0
                        s12 = stress(i)%at(4, j)
                    ! general case
                    case (6)
                        s11 = stress(i)%at(1, j)
                        s22 = stress(i)%at(2, j)
                        s33 = stress(i)%at(3, j)
                        s23 = stress(i)%at(4, j)
                        s31 = stress(i)%at(5, j)
                        s12 = stress(i)%at(6, j)
                    ! otherwise
                    case default
                        error stop ERROR_UNDEFINED_SECTION_TYPE
                end select
                
                ! build matrix
                matrix = new_matrix(3, 3)
                matrix%at(1, :) = [s11, s12, s31]
                matrix%at(2, :) = [s12, s22, s23]
                matrix%at(3, :) = [s31, s23, s33]
                
                ! compute principal stresses
                eigenvalues = eigen(matrix)
                s1          = eigenvalues%at(3)
                s2          = eigenvalues%at(2)
                s3          = eigenvalues%at(1)
                sMajor      = eigenvalues%at(maxloc(abs(eigenvalues%at(:)), dim=1))
                
                ! compute equivalent stresses
                sTresca = s1 - s3
                sMises  = sqrt(((s1 - s2)**2 + (s2 - s3)**2 + (s3 - s1)**2)/2.0)
                sPress  = -(s11 + s22 + s33)/3.0
                
                ! store results
                extra(i)%at(:, j) = [s11, s22, s33, s23, s31, s12, s1, s2, s3, sMajor, sTresca, sMises, sPress]
            end do
        end do
    end subroutine
    
    ! Description:
    ! Extrapolation from integration points to element nodes.
    subroutine extrapolate(n_elements, elements, at_ips, at_nodes)
        ! procedure arguments
        integer,         intent(in)    :: n_elements  ! number of elements
        type(t_element), intent(in)    :: elements(:) ! mesh elements
        type(t_matrix),  intent(in)    :: at_ips(:)   ! values at element integration points
        type(t_matrix),  intent(inout) :: at_nodes(:) ! values at element nodes
        
        ! additional variables
        type(t_matrix) :: E ! extrapolation matrix
        integer        :: i ! loop counter
        
        ! perform extrapolation
        do i = 1, n_elements
            E = extrapolation_matrix(elements(i))
            at_nodes(i) = multiply(E, at_ips(i), transposeB=.true.)
            call at_nodes(i)%T ! transpose matrix
        end do
    end subroutine
    
    ! Description:
    ! Final nodal average (smoothing).
    type(t_matrix) function average(mesh, at_elements, n_components) result(at_mesh)
        ! procedure arguments
        type(t_mesh),   intent(in) :: mesh           ! finite element mesh
        type(t_matrix), intent(in) :: at_elements(:) ! values at element nodes
        integer,        intent(in) :: n_components   ! number of components
        
        ! additional variables
        integer :: i ! loop counter
        
        ! initialize matrix
        at_mesh = new_matrix(mesh%n_nodes, n_components)
        
        ! perform smoothing
        do i = 1, mesh%n_elements
            at_mesh%at(mesh%elements(i)%i_nodes, :) = at_mesh%at(mesh%elements(i)%i_nodes, :) + transpose(at_elements(i)%at(:, :))
        end do
        do i = 1, n_components
            at_mesh%at(:, i) = at_mesh%at(:, i)/mesh%e_counts(:)
        end do
    end function
    
    ! Description:
    ! Converts a global vector into a matrix of values per node.
    type(t_matrix) function convert_vector(m_space, n_nodes, nodes, Va, Vb) result(matrix)
        ! procedure arguments
        integer,        intent(in) :: m_space  ! modeling space
        integer,        intent(in) :: n_nodes  ! number of nodes
        type(t_node),   intent(in) :: nodes(:) ! mesh nodes
        type(t_vector), intent(in) :: Va, Vb   ! global vector
        
        ! additional variables
        real    :: x, y, z   ! components
        real    :: magnitude ! magnitude (norm)
        integer :: i         ! loop counter
        
        ! initialize results matrix
        matrix = new_matrix(n_nodes, 4) ! x, y, z, magnitude
        
        ! build matrix
        do i = 1, n_nodes
            ! get individual components
            if (nodes(i)%dofs(1) > 0) then; x = Va%at(nodes(i)%dofs(1)); else; x = Vb%at(abs(nodes(i)%dofs(1))); end if
            if (nodes(i)%dofs(2) > 0) then; y = Va%at(nodes(i)%dofs(2)); else; y = Vb%at(abs(nodes(i)%dofs(2))); end if
            if (m_space == 3) then
                if (nodes(i)%dofs(3) > 0) then; z = Va%at(nodes(i)%dofs(3)); else; z = Vb%at(abs(nodes(i)%dofs(3))); end if
            else
                z = 0.0
            end if
            
            ! compute magnitude
            magnitude = sqrt(x*x + y*y + z*z)
            
            ! store results
            matrix%at(i, :) = [x, y, z, magnitude]
        end do
    end function
    
    ! Description:
    ! Builds a global system matrix based on the specified element matrices.
    subroutine local_to_global_matrix(n_adofs, n_idofs, n_elements, elements, As, Aaa, Aab)
        ! procedure arguments
        integer,         intent(in)  :: n_adofs     ! number of active degrees of freedom
        integer,         intent(in)  :: n_idofs     ! number of inactive degrees of freedom
        integer,         intent(in)  :: n_elements  ! number of elements
        type(t_element), intent(in)  :: elements(:) ! mesh elements
        type(t_matrix),  intent(in)  :: As(:)       ! the element matrices
        type(t_sparse),  intent(out) :: Aaa, Aab    ! the global matrix
        
        ! additional variables
        integer :: il, jl ! local indices
        integer :: ig, jg ! global indices
        integer :: k      ! element index
        
        ! initialize global sparse matrices
        Aaa = new_sparse(n_adofs, n_adofs)
        Aab = new_sparse(n_adofs, n_idofs)
        
        ! local to global
        do k = 1, n_elements
            do il = 1, elements(k)%n_edofs
                ig = elements(k)%dofs(il)
                if (ig > 0) then
                    do jl = 1, elements(k)%n_edofs
                        jg = elements(k)%dofs(jl)
                        if (jg > 0) then
                            call Aaa%add(ig, jg, As(k)%at(il, jl))
                        else
                            call Aab%add(ig, abs(jg), As(k)%at(il, jl))
                        end if
                    end do
                end if
            end do
        end do
        
        ! use compact storage
        call Aaa%to_csr()
        call Aab%to_csr()
    end subroutine
    
    ! Description:
    ! Builds a global system vector based on the specified element vectors.
    subroutine local_to_global_vector(n_adofs, n_idofs, n_elements, elements, Vs, Vaa, Vab)
        ! procedure arguments
        integer,         intent(in)  :: n_adofs     ! number of active degrees of freedom
        integer,         intent(in)  :: n_idofs     ! number of inactive degrees of freedom
        integer,         intent(in)  :: n_elements  ! number of elements
        type(t_element), intent(in)  :: elements(:) ! mesh elements
        type(t_vector),  intent(in)  :: Vs(:)       ! the element vectors
        type(t_vector),  intent(out) :: Vaa, Vab    ! the global vector
        
        ! additional variables
        integer :: il ! local index
        integer :: ig ! global index
        integer :: k  ! element index
        
        ! initialize global vectors
        Vaa = new_vector(n_adofs)
        Vab = new_vector(n_idofs)
        
        ! local to global
        do k = 1, n_elements
            do il = 1, elements(k)%n_edofs
                ig = elements(k)%dofs(il)
                if (ig > 0) then
                    Vaa%at(ig) = Vaa%at(ig) + Vs(k)%at(il)
                else
                    Vab%at(ig) = Vab%at(ig) + Vs(k)%at(abs(il))
                end if
            end do
        end do
        
    end subroutine
    
end module
