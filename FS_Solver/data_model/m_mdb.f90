! Description:
! Definition of a finite element model database.
module m_mdb
    use m_mesh
    use m_nset
    use m_eset
    use m_sset
    use m_material
    use m_section
    use m_cload
    use m_sload
    use m_bload
    use m_boundary
    implicit none
    
    private
    public t_mdb, new_mdb
    
    type t_mdb
        integer                       :: n_adofs       ! number of active DOFs
        integer                       :: n_idofs       ! number of inactive DOFs
        integer                       :: n_nsets       ! number of node sets
        integer                       :: n_esets       ! number of element sets
        integer                       :: n_ssets       ! number of surface sets
        integer                       :: n_materials   ! number of materials
        integer                       :: n_sections    ! number of sections
        integer                       :: n_cloads      ! number of concentrated loads
        integer                       :: n_sloads      ! number of surface loads
        integer                       :: n_bloads      ! number of body loads
        integer                       :: n_boundaries  ! number of boundary conditions
        type(t_mesh)                  :: mesh          ! finite element mesh
        type(t_nset),     allocatable :: nsets(:)      ! node sets
        type(t_eset),     allocatable :: esets(:)      ! element sets
        type(t_sset),     allocatable :: ssets(:)      ! surface sets
        type(t_material), allocatable :: materials(:)  ! materials
        type(t_section),  allocatable :: sections(:)   ! sections
        type(t_cload),    allocatable :: cloads(:)     ! concentrated loads
        type(t_sload),    allocatable :: sloads(:)     ! surface loads
        type(t_bload),    allocatable :: bloads(:)     ! body loads
        type(t_boundary), allocatable :: boundaries(:) ! boundary conditions
    contains
        procedure :: build_dofs
        final     :: destructor
    end type
    
    interface new_mdb
        module procedure :: constructor
    end interface
    
    contains
    
    ! Description:
    ! Finite element model database constructor.
    type(t_mdb) function constructor(n_nsets, n_esets, n_ssets, n_materials, n_sections, n_cloads, n_sloads, n_bloads, n_boundaries, mesh) result(self)
        integer,      intent(in) :: n_nsets      ! number of node sets
        integer,      intent(in) :: n_esets      ! number of element sets
        integer,      intent(in) :: n_ssets      ! number of surface sets
        integer,      intent(in) :: n_materials  ! number of materials
        integer,      intent(in) :: n_sections   ! number of sections
        integer,      intent(in) :: n_cloads     ! number of concentrated loads
        integer,      intent(in) :: n_sloads     ! number of surface loads
        integer,      intent(in) :: n_bloads     ! number of body loads
        integer,      intent(in) :: n_boundaries ! number of boundary conditions
        type(t_mesh), intent(in) :: mesh         ! finite element mesh
        self%n_nsets      = n_nsets
        self%n_esets      = n_esets
        self%n_ssets      = n_ssets
        self%n_materials  = n_materials
        self%n_sections   = n_sections
        self%n_cloads     = n_cloads
        self%n_sloads     = n_sloads
        self%n_bloads     = n_bloads
        self%n_boundaries = n_boundaries
        self%mesh         = mesh
        allocate(self%nsets(self%n_nsets))
        allocate(self%esets(self%n_esets))
        allocate(self%ssets(self%n_ssets))
        allocate(self%materials(self%n_materials))
        allocate(self%sections(self%n_sections))
        allocate(self%cloads(self%n_cloads))
        allocate(self%sloads(self%n_sloads))
        allocate(self%bloads(self%n_bloads))
        allocate(self%boundaries(self%n_boundaries))
    end function
    
    ! Description:
    ! Finite element model database destructor.
    subroutine destructor(self)
        type(t_mdb), intent(inout) :: self
        if (allocated(self%nsets))      deallocate(self%nsets)
        if (allocated(self%esets))      deallocate(self%esets)
        if (allocated(self%ssets))      deallocate(self%ssets)
        if (allocated(self%materials))  deallocate(self%materials)
        if (allocated(self%sections))   deallocate(self%sections)
        if (allocated(self%cloads))     deallocate(self%cloads)
        if (allocated(self%sloads))     deallocate(self%sloads)
        if (allocated(self%bloads))     deallocate(self%bloads)
        if (allocated(self%boundaries)) deallocate(self%boundaries)
    end subroutine
    
    ! Description:
    ! Build element DOFs (algebraic connectivity).
    subroutine build_dofs(self)
        class(t_mdb), intent(inout) :: self
        integer :: i, j, k, l
        
        ! identify inactive DOFs
        do i = 1, self%mesh%n_nodes
            do j = 1, self%mesh%m_space
                do k = 1, self%n_boundaries
                    do l = 1, self%nsets(self%boundaries(k)%i_nset)%n_nodes
                        if (self%nsets(self%boundaries(k)%i_nset)%i_nodes(l) == i .AND. self%boundaries(k)%active(j)) then
                            self%mesh%nodes(i)%dofs(j) = -1
                        end if
                    end do
                end do
            end do
        end do
        
        ! count DOFs
        self%n_adofs = 0
        self%n_idofs = 0
        do i = 1, self%mesh%n_nodes
            do j = 1, self%mesh%m_space
                if (self%mesh%nodes(i)%dofs(j) == -1) then
                    self%n_idofs = self%n_idofs + 1
                    self%mesh%nodes(i)%dofs(j) = -self%n_idofs
                else
                    self%n_adofs = self%n_adofs + 1
                    self%mesh%nodes(i)%dofs(j) = +self%n_adofs
                end if
            end do
        end do
        
        ! assign to elements
        do i = 1, self%mesh%n_elements
            j = 0
            do k = 1, self%mesh%elements(i)%n_nodes
                do l = 1, self%mesh%elements(i)%n_ndofs
                    j = j + 1
                    self%mesh%elements(i)%dofs(j) = self%mesh%nodes(self%mesh%elements(i)%i_nodes(k))%dofs(l)
                end do
            end do
        end do
    end subroutine
    
end module
